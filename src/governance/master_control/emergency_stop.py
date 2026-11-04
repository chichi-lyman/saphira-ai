from dataclasses import dataclass
from datetime import datetime,timezone
@dataclass(frozen=True)
class StopState:
    engaged:bool
    reason:str|None
    changed_at:datetime
class EmergencyStop:
    def __init__(self,store): self.store=store
    def engage(self,reason,*,authorized):
        if not authorized: raise PermissionError("Master authorization required")
        state=StopState(True,reason,datetime.now(timezone.utc)); self.store.set(state); return state
    def release(self,*,authorized):
        if not authorized: raise PermissionError("Master authorization required")
        state=StopState(False,None,datetime.now(timezone.utc)); self.store.set(state); return state
    def assert_running(self):
        state=self.store.get()
        if state and state.engaged: raise RuntimeError("Emergency stop engaged")
