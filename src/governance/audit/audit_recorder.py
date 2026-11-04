"""Hash-chained audit events; production store must append atomically and be append-only."""
from dataclasses import dataclass
from datetime import datetime,timezone
import hashlib,json
from threading import Lock
@dataclass(frozen=True)
class AuditEvent:
    sequence:int
    timestamp:str
    event:str
    actor:str
    command_id:str
    outcome:str
    details:dict
    previous_hash:str
    event_hash:str
class InMemoryAuditStore:
    """Test-only store. Production adapter must enforce append-only retention and backup."""
    def __init__(self): self.events=[]; self.lock=Lock()
    def all(self):
        with self.lock: return tuple(self.events)
    def append_if_head(self,event,expected_previous_hash):
        with self.lock:
            current=self.events[-1].event_hash if self.events else "0"*64
            if current!=expected_previous_hash: return False
            self.events.append(event); return True
class AuditRecorder:
    def __init__(self,store): self.store=store
    def record(self,*,event,actor,command_id,outcome,details=None):
        prior=self.store.all()
        previous=prior[-1].event_hash if prior else "0"*64
        body={"sequence":len(prior)+1,"timestamp":datetime.now(timezone.utc).isoformat(),
              "event":event,"actor":actor,"command_id":command_id,"outcome":outcome,
              "details":details or {},"previous_hash":previous}
        digest=hashlib.sha256(json.dumps(body,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
        item=AuditEvent(**body,event_hash=digest)
        if not self.store.append_if_head(item,previous):
            raise RuntimeError("Audit append conflict; retry with current chain head")
        return item
