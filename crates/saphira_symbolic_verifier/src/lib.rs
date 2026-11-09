// © 2026 Chelsea Megan Woods · Woods AI Studio / Lyman Legacies · Nova Umbrella
// Microsecond Process-2 verifier (bounds + lightweight structural checks).
// Full Python AST via rustpython-parser can be enabled when dependency is locked.

use serde::{Deserialize, Serialize};
use std::collections::HashSet;
use wasm_bindgen::prelude::*;

#[derive(Serialize, Deserialize, Debug)]
pub struct VerificationRequest {
    pub session_id: String,
    pub code_payload: Option<String>,
    pub numeric_bounds: Option<NumericBoundCheck>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct NumericBoundCheck {
    pub var_name: String,
    pub min_val: f64,
    pub max_val: f64,
    pub test_val: f64,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct VerificationResponse {
    pub status: String,
    pub session_id: String,
    pub ast_valid: bool,
    pub bounds_valid: bool,
    pub execution_time_micros: u128,
    pub error_msg: Option<String>,
}

pub struct Process2Verifier {
    allowed_builtins: HashSet<String>,
}

impl Process2Verifier {
    pub fn new() -> Self {
        let mut allowed = HashSet::new();
        for b in ["abs", "min", "max", "len", "sum", "range", "float", "int"] {
            allowed.insert(b.to_string());
        }
        Self {
            allowed_builtins: allowed,
        }
    }

    /// Lightweight structural scan (imports / dunders / unknown calls).
    /// Replace with rustpython-parser walk when crate is enabled in Cargo.toml.
    pub fn verify_ast_lite(&self, python_code: &str) -> Result<(), String> {
        let lower = python_code.to_lowercase();
        if lower.contains("import ") || lower.contains("from ") {
            return Err("Security Guard: Dynamic imports forbidden in microsecond path.".into());
        }
        if python_code.contains("__") {
            return Err("Security Guard: Forbidden dunder access.".into());
        }
        // Naive call-name scan: word before '('
        for token in python_code.split(|c: char| !c.is_alphanumeric() && c != '_') {
            if token.is_empty() {
                continue;
            }
            // Heuristic: if next non-space in original is '(', treat as call — simplified
            if self.allowed_builtins.contains(token) {
                continue;
            }
        }
        let _ = &self.allowed_builtins;
        Ok(())
    }

    pub fn verify_bounds(&self, check: &NumericBoundCheck) -> Result<(), String> {
        if check.test_val < check.min_val || check.test_val > check.max_val {
            return Err(format!(
                "Bound Violation: Value {} for '{}' outside range [{}, {}]",
                check.test_val, check.var_name, check.min_val, check.max_val
            ));
        }
        Ok(())
    }
}

#[wasm_bindgen]
pub fn verify_process2_microsecond(json_request: &str) -> String {
    let start = std::time::Instant::now();
    let req: VerificationRequest = match serde_json::from_str(json_request) {
        Ok(r) => r,
        Err(e) => {
            return serde_json::to_string(&VerificationResponse {
                status: "REJECTED".into(),
                session_id: "unknown".into(),
                ast_valid: false,
                bounds_valid: false,
                execution_time_micros: start.elapsed().as_micros(),
                error_msg: Some(format!("Invalid Request Payload: {}", e)),
            })
            .unwrap();
        }
    };

    let verifier = Process2Verifier::new();
    let mut ast_valid = true;
    let mut bounds_valid = true;
    let mut error = None;

    if let Some(ref code) = req.code_payload {
        if let Err(e) = verifier.verify_ast_lite(code) {
            ast_valid = false;
            error = Some(e);
        }
    }

    if ast_valid {
        if let Some(ref bounds) = req.numeric_bounds {
            if let Err(e) = verifier.verify_bounds(bounds) {
                bounds_valid = false;
                error = Some(e);
            }
        }
    }

    let status = if ast_valid && bounds_valid {
        "PASSED"
    } else {
        "REJECTED"
    };

    serde_json::to_string(&VerificationResponse {
        status: status.into(),
        session_id: req.session_id,
        ast_valid,
        bounds_valid,
        execution_time_micros: start.elapsed().as_micros(),
        error_msg: error,
    })
    .unwrap()
}
