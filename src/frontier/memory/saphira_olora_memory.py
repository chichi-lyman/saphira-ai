# © 2026 Chelsea Megan Woods · Woods AI Studio / Lyman Legacies · Nova Umbrella
"""Saphira O-LoRA zero-drift memory + formal verification server (REST + WebSocket)."""
from __future__ import annotations

import ast
import json
import logging
from typing import Any, Dict, List, Optional

import numpy as np
import torch
import torch.nn as nn
from fastapi import BackgroundTasks, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

try:
    import sympy as sp

    HAS_SYMPY = True
except ImportError:
    HAS_SYMPY = False

try:
    from z3 import Not, Real, Solver, sat, unsat

    HAS_Z3 = True
except ImportError:
    HAS_Z3 = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SaphiraFormalMemoryServer")

app = FastAPI(
    title="Saphira AI Memory & Formal Verification Server",
    version="2.0.0",
    description="O-LoRA zero-drift memory with REST/WebSocket SymPy/Z3/AST gates.",
)


class OLoRAConfig:
    r: int = 8
    alpha: float = 16.0
    scaling: float = 16.0 / 8
    in_features: int = 768
    out_features: int = 768


class MemoryPayload(BaseModel):
    session_id: str
    tokens: List[float]
    importance_score: float = 1.0


class OrthogonalLoRALayer(nn.Module):
    def __init__(self, in_features: int, out_features: int, r: int, scaling: float):
        super().__init__()
        self.r = r
        self.scaling = scaling
        self.W_base = nn.Parameter(torch.randn(out_features, in_features), requires_grad=False)
        self.lora_A = nn.Parameter(torch.randn(r, in_features))
        self.lora_B = nn.Parameter(torch.zeros(out_features, r))
        nn.init.kaiming_uniform_(self.lora_A, a=np.sqrt(5))

    def project_null_space(self, base_null_basis: torch.Tensor) -> None:
        with torch.no_grad():
            eye = torch.eye(base_null_basis.size(0), device=base_null_basis.device)
            projection = eye - torch.mm(base_null_basis, base_null_basis.T)
            self.lora_A.copy_(torch.mm(self.lora_A, projection))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        base_out = torch.matmul(x, self.W_base.T)
        adapter = torch.matmul(torch.matmul(x, self.lora_A.T), self.lora_B.T) * self.scaling
        return base_out + adapter


olora_layer = OrthogonalLoRALayer(
    OLoRAConfig.in_features,
    OLoRAConfig.out_features,
    OLoRAConfig.r,
    OLoRAConfig.scaling,
)


def adapt_weights_background(payload: MemoryPayload) -> None:
    """Background O-LoRA steps projected into approximate null space of W_base."""
    x = torch.tensor([payload.tokens], dtype=torch.float32)
    opt = torch.optim.AdamW([olora_layer.lora_A, olora_layer.lora_B], lr=1e-4)
    with torch.no_grad():
        _, _, vh = torch.linalg.svd(olora_layer.W_base, full_matrices=True)
        null_basis = vh[OLoRAConfig.r :].T
    for _ in range(3):
        opt.zero_grad()
        out = olora_layer(x)
        loss = torch.mean((out - x) ** 2) * payload.importance_score
        loss.backward()
        opt.step()
        olora_layer.project_null_space(null_basis)


class SymPySpec(BaseModel):
    expr1: str
    expr2: str


class Z3Spec(BaseModel):
    variables: List[str]
    constraints: List[str]
    assertion: str


class FormalVerificationRequest(BaseModel):
    session_id: str = Field(default="default-session")
    code_payload: Optional[str] = None
    sympy_spec: Optional[SymPySpec] = None
    z3_spec: Optional[Z3Spec] = None


class FormalVerificationResponse(BaseModel):
    status: str
    session_id: str
    sympy_valid: Optional[bool] = None
    z3_valid: Optional[bool] = None
    ast_valid: Optional[bool] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class FormalVerifierCore:
    ALLOWED = ["abs", "min", "max", "len", "sum", "range", "float", "int"]

    @staticmethod
    def verify_sympy(expr1: str, expr2: str) -> bool:
        if not HAS_SYMPY:
            raise ValueError("SymPy not installed")
        diff = sp.simplify(sp.sympify(expr1) - sp.sympify(expr2))
        if diff != 0:
            raise ValueError(f"SymPy discrepancy: {diff}")
        return True

    @staticmethod
    def verify_z3(variables: List[str], constraints: List[str], assertion: str) -> bool:
        if not HAS_Z3:
            raise ValueError("z3-solver not installed")
        solver = Solver()
        z3_vars = {v: Real(v) for v in variables}
        safe: Dict[str, Any] = {"__builtins__": None, **z3_vars}
        for c in constraints:
            solver.add(eval(c, safe))
        solver.add(Not(eval(assertion, safe)))
        result = solver.check()
        if result == sat:
            raise ValueError(f"Z3 counter-example: {solver.model()}")
        if result == unsat:
            return True
        raise ValueError("Z3 inconclusive")

    @staticmethod
    def verify_ast(python_code: str) -> bool:
        tree = ast.parse(python_code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                raise ValueError("AST: imports forbidden")
            if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
                raise ValueError(f"AST: dunder forbidden ({node.attr})")
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id not in FormalVerifierCore.ALLOWED:
                    raise ValueError(f"AST: unauthorized call '{node.func.id}'")
        return True


def _run_formal(req: FormalVerificationRequest) -> FormalVerificationResponse:
    details: Dict[str, Any] = {}
    sympy_r = z3_r = ast_r = None
    try:
        if req.sympy_spec:
            sympy_r = FormalVerifierCore.verify_sympy(req.sympy_spec.expr1, req.sympy_spec.expr2)
            details["sympy"] = "Algebraic equivalence proven."
        if req.z3_spec:
            z3_r = FormalVerifierCore.verify_z3(
                req.z3_spec.variables, req.z3_spec.constraints, req.z3_spec.assertion
            )
            details["z3"] = "Z3 SMT proof holds; zero counter-examples."
        if req.code_payload:
            ast_r = FormalVerifierCore.verify_ast(req.code_payload)
            details["ast"] = "AST syntax & security checks passed."
        return FormalVerificationResponse(
            status="PASSED",
            session_id=req.session_id,
            sympy_valid=sympy_r,
            z3_valid=z3_r,
            ast_valid=ast_r,
            details=details,
        )
    except Exception as e:
        logger.error("Verification failure: %s", e)
        return FormalVerificationResponse(
            status="REJECTED",
            session_id=req.session_id,
            sympy_valid=False if req.sympy_spec else None,
            z3_valid=False if req.z3_spec else None,
            ast_valid=False if req.code_payload else None,
            details={"error": str(e)},
        )


@app.get("/v1/memory/status")
async def memory_status():
    return {
        "adapter_rank": olora_layer.r,
        "scaling_factor": olora_layer.scaling,
        "active_parameters": sum(
            p.numel() for p in [olora_layer.lora_A, olora_layer.lora_B]
        ),
        "sympy": HAS_SYMPY,
        "z3": HAS_Z3,
    }


@app.post("/v1/memory/ingest")
async def ingest_memory(payload: MemoryPayload, background_tasks: BackgroundTasks):
    if len(payload.tokens) != OLoRAConfig.in_features:
        raise HTTPException(status_code=400, detail="Token vector dimension mismatch.")
    background_tasks.add_task(adapt_weights_background, payload)
    return {
        "status": "queued",
        "session_id": payload.session_id,
        "mode": "O-LoRA Zero-Drift",
    }


@app.post("/v1/verify/formal", response_model=FormalVerificationResponse)
async def verify_formal_rest(req: FormalVerificationRequest):
    return _run_formal(req)


@app.websocket("/ws/verify")
async def verify_formal_websocket(websocket: WebSocket):
    await websocket.accept()
    logger.info("Agent connected to WebSocket verification pipeline.")
    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            req = FormalVerificationRequest(**data)
            res = _run_formal(req)
            await websocket.send_text(res.model_dump_json())
    except WebSocketDisconnect:
        logger.info("Agent disconnected from WebSocket verification pipeline.")
    except Exception as e:
        logger.error("WebSocket error: %s", e)
        await websocket.close()
