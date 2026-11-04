from dataclasses import replace
from src.governance.authorization.rbac import Principal,RBAC
from src.governance.authorization.policy_engine import PolicyEngine,Decision
from src.governance.audit.audit_recorder import AuditRecorder,InMemoryAuditStore
from src.governance.audit.audit_integrity import verify_chain
from src.governance.authentication.admin_mfa import verify_totp

def test_rbac_denies_unknown_and_privileged_permissions():
    principal=Principal("u1","user",("user",))
    assert RBAC().allows(principal,"profile:read")
    assert not RBAC().allows(principal,"keys:rotate")
    assert not RBAC().allows(principal,"unknown:action")
def test_privileged_permission_requires_master_approval():
    result=PolicyEngine().evaluate(Principal("u1","user",("user",)),"task:cancel")
    assert result.decision is Decision.REQUIRE_APPROVAL
def test_audit_chain_detects_tampering():
    store=InMemoryAuditStore(); recorder=AuditRecorder(store)
    recorder.record(event="CHECK",actor="agent",command_id="t1",outcome="DENIED")
    recorder.record(event="CHECK",actor="agent",command_id="t2",outcome="ALLOWED")
    assert verify_chain(store.all())
    altered=replace(store.all()[0],outcome="ALTERED")
    assert not verify_chain((altered,store.all()[1]))
def test_totp_rejects_malformed_code():
    assert not verify_totp("JBSWY3DPEHPK3PXP","abc")
