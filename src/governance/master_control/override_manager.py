from ..errors import AuthorizationDenied
class OverrideManager:
    def __init__(self,gateway,executor,audit): self.gateway=gateway; self.executor=executor; self.audit=audit
    def execute(self,envelope,*,mfa_code,permission,validate,verify_result):
        command_id=getattr(envelope,"command_id","unknown")
        try:
            command_id=self.gateway.authorize(envelope,mfa_code=mfa_code,required_scope=permission)
            if not validate(envelope): raise AuthorizationDenied("State validation failed")
            result=self.executor(envelope); verified=bool(verify_result(envelope,result))
            self.audit.record(event="MASTER_OVERRIDE",actor=envelope.administrator_id,command_id=command_id,outcome="VERIFIED" if verified else "UNVERIFIED",details={"permission":permission,"target":envelope.target,"action":envelope.action})
            if not verified: raise AuthorizationDenied("Override could not be verified")
            return result
        except Exception as exc:
            self.audit.record(event="MASTER_OVERRIDE",actor=getattr(envelope,"administrator_id","unknown"),command_id=command_id,outcome="FAILED_OR_DENIED",details={"error_type":type(exc).__name__})
            raise
