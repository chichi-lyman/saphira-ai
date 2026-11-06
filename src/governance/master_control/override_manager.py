"""Privileged override execution with pre-action audit intent and post-action verification."""
from ..errors import AuthorizationDenied
class OverrideManager:
    def __init__(self,gateway,executor,audit):
        self.gateway,self.executor,self.audit=gateway,executor,audit
    def execute(self,envelope,*,mfa_code,permission,validate,verify_result):
        command_id=getattr(envelope,"command_id","unknown")
        actor=getattr(envelope,"administrator_id","unknown")
        try:
            command_id=self.gateway.authorize(envelope,mfa_code=mfa_code,required_scope=permission)
            if not validate(envelope): raise AuthorizationDenied("Protected-state validation failed")
            # If this durable audit write fails, execution does not proceed.
            self.audit.record(event="MASTER_OVERRIDE_INTENT",actor=actor,command_id=command_id,
                              outcome="AUTHORIZED_PENDING",details={"permission":permission,
                              "target":envelope.target,"action":envelope.action})
            result=self.executor(envelope)
            verified=bool(verify_result(envelope,result))
            self.audit.record(event="MASTER_OVERRIDE_RESULT",actor=actor,command_id=command_id,
                              outcome="VERIFIED" if verified else "UNVERIFIED",
                              details={"permission":permission,"target":envelope.target,
                              "action":envelope.action})
            if not verified: raise AuthorizationDenied("Override result could not be verified")
            return result
        except Exception as exc:
            # A failed audit sink must never turn a denied request into an allowed one.
            try:
                self.audit.record(event="MASTER_OVERRIDE_FAILURE",actor=actor,command_id=command_id,
                                  outcome="FAILED_OR_DENIED",details={"error_type":type(exc).__name__})
            except Exception:
                pass
            raise
