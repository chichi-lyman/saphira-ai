# © 2026 Chelsea Megan Woods · Woods AI Studio / Lyman Legacies · Nova Umbrella
"""Dual-process formal verifier: AST security + optional SymPy / Z3 gates."""
from __future__ import annotations

import ast
import re
from typing import Any, Dict, List, Optional, Tuple

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


class FormalVerificationError(Exception):
    """Raised when Process-2 formal logic or mathematical verification fails."""


class DualProcessFormalVerifier:
    def __init__(self, allowed_builtins: Optional[List[str]] = None):
        self.allowed_builtins = allowed_builtins or [
            "abs",
            "min",
            "max",
            "len",
            "sum",
            "range",
            "float",
            "int",
        ]

    def process_1_extract(self, payload: str) -> str:
        match = re.search(r"```python\n(.*?)\n```", payload, re.DOTALL)
        return match.group(1).strip() if match else payload.strip()

    def verify_sympy_identity(self, expr1: str, expr2: str) -> bool:
        if not HAS_SYMPY:
            raise FormalVerificationError("SymPy not installed")
        try:
            diff = sp.simplify(sp.sympify(expr1) - sp.sympify(expr2))
            if diff != 0:
                raise FormalVerificationError(
                    f"SymPy: '{expr1}' not equivalent to '{expr2}' (diff={diff})"
                )
            return True
        except FormalVerificationError:
            raise
        except Exception as e:
            raise FormalVerificationError(f"SymPy parse error: {e}") from e

    def verify_z3_bounds(
        self, variables: List[str], constraints: List[str], assertion: str
    ) -> bool:
        if not HAS_Z3:
            raise FormalVerificationError("z3-solver not installed")
        try:
            solver = Solver()
            z3_vars = {v: Real(v) for v in variables}
            safe: Dict[str, Any] = {"__builtins__": None, **z3_vars}
            for c in constraints:
                solver.add(eval(c, safe))
            solver.add(Not(eval(assertion, safe)))
            result = solver.check()
            if result == sat:
                raise FormalVerificationError(f"Z3 counter-example: {solver.model()}")
            if result == unsat:
                return True
            raise FormalVerificationError("Z3 inconclusive")
        except FormalVerificationError:
            raise
        except Exception as e:
            raise FormalVerificationError(f"Z3 failure: {e}") from e

    def verify_ast(self, python_code: str) -> ast.AST:
        try:
            tree = ast.parse(python_code)
        except SyntaxError as e:
            raise FormalVerificationError(f"AST syntax: {e}") from e
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                raise FormalVerificationError("AST policy: imports forbidden")
            if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
                raise FormalVerificationError(
                    f"AST policy: dunder forbidden ({node.attr})"
                )
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id not in self.allowed_builtins:
                    raise FormalVerificationError(
                        f"AST policy: unauthorized call '{node.func.id}'"
                    )
        return tree

    def execute_contract(
        self,
        raw_llm_output: str,
        verification_specs: Optional[Dict[str, Any]] = None,
        execution_context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Dict[str, Any], str]:
        specs = verification_specs or {}
        code = self.process_1_extract(raw_llm_output)
        if "sympy_equivalence" in specs:
            s = specs["sympy_equivalence"]
            self.verify_sympy_identity(s["expr1"], s["expr2"])
        if "z3_bounds" in specs:
            s = specs["z3_bounds"]
            self.verify_z3_bounds(s["variables"], s["constraints"], s["assertion"])
        tree = self.verify_ast(code)
        compiled = compile(tree, "<formal_verifier>", "exec")
        bi = __builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__
        global_scope: Dict[str, Any] = {
            "__builtins__": {b: bi[b] for b in self.allowed_builtins if b in bi}
        }
        if execution_context:
            global_scope.update(execution_context)
        local: Dict[str, Any] = {}
        exec(compiled, global_scope, local)
        return local, "SUCCESS: formally verified & executed"


if __name__ == "__main__":
    v = DualProcessFormalVerifier()
    print("SymPy:", v.verify_sympy_identity("(x+y)**2", "x**2+2*x*y+y**2"))
    print(
        "Z3:",
        v.verify_z3_bounds(["x", "y"], ["x > 5", "y > 10"], "x + y > 15"),
    )
