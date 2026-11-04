"""Emergency stop; engagement and release require a verified master command."""
from dataclasses import dataclass
from datetime import datetime,timezone
@dataclass(frozen=True)
class StopState:
    engaged:bool
    reason:str|None
    changed_at:datetime
class EmergencyStop:
    def __init__(self,store,gateway): self.store=store; self.gateway=gateway
    def engage(self,envelope,*,mfa_code,reason):
        self.gateway.authorize(envelope,mfa_code=mfa_code,required_scope="emergency:stop")
        state=StopState(True,reason,datetime.now(timezone.utc)); self.store.set(state); return state
    def release(self,envelope,*,mfa_code):
        self.gateway.authorize(envelope,mfa_code=mfa_code,required_scope="emergency:stop")
        state=StopState(False,None,datetime.now(timezone.utc)); self.store.set(state); return state
    def assert_running(self):
        state=self.store.get()
        if state and state.engaged: raise RuntimeError("Emergency stop engaged; execution blocked")
