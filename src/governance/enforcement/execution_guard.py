from ..errors import AuthorizationDenied
class ExecutionGuard:
    def __init__(self,*,policy_engine,emergency_stop,delegated_credentials,audit): self.policy=policy_engine; self.stop=emergency_stop; self.grants=delegated_credentials; self.audit=audit
    def authorize_user(self,principal,permission,resource=None):
        self.stop.assert_running(); self.policy.require_standard(principal,permission,resource)
    def authorize_agent(self,*,agent_id,task_id,token,permission):
        self.stop.assert_running()
        if not self.grants.validate(token,agent_id=agent_id,task_id=task_id,permission=permission):
            self.audit.record(event="AGENT_EXECUTION_DENIED",actor=agent_id,command_id=task_id,outcome="DENIED",details={"permission":permission})
            raise AuthorizationDenied("Agent grant missing, expired, revoked, or out of scope")
        return True
