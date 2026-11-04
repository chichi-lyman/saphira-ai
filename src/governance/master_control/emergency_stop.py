"""Durable emergency stop. Both engagement and release require a signed master command."""
from dataclasses import dataclass
from datetime import datetime,timezone
@dataclass(frozen=True)
class StopState:
    engaged:bool
    reason:str|None
    changed_at:datetime
class EmergencyStop:
    def __init__(self,store,gateway,audit):
        self.store,self.gateway,self.audit=store,gateway,audit
    def engage(self,envelope,*,mfa_code,reason):
        command_id=self.gateway.authorize(envelope,mfa_code=mfa_code,required_scope="emergency:stop")
        state=StopState(True,reason,datetime.now(timezone.utc))
        self.store.set(state)
        self.audit.record(event="EMERGENCY_STOP_ENGAGED",actor=envelope.administrator_id,
                          command_id=command_id,outcome="APPLIED",details={"reason":reason})
        return state
    def release(self,envelope,*,mfa_code):
        command_id=self.gateway.authorize(envelope,mfa_code=mfa_code,required_scope="emergency:stop")
        state=StopState(False,None,datetime.now(timezone.utc))
        self.store.set(state)
        self.audit.record(event="EMERGENCY_STOP_RELEASED",actor=envelope.administrator_id,
                          command_id=command_id,outcome="APPLIED")
        return state
    def assert_running(self):
        state=self.store.get()
        if state and state.engaged:
            raise RuntimeError("Emergency stop engaged; execution blocked")
