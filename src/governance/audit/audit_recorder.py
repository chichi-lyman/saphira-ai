from dataclasses import dataclass
from datetime import datetime,timezone
import hashlib,json
@dataclass(frozen=True)
class AuditEvent:
    sequence:int; timestamp:str; event:str; actor:str; command_id:str; outcome:str; details:dict; previous_hash:str; event_hash:str
class InMemoryAuditStore:
    def __init__(self): self.events=[]
    def append(self,event): self.events.append(event)
    def all(self): return tuple(self.events)
class AuditRecorder:
    def __init__(self,store): self.store=store
    def record(self,*,event,actor,command_id,outcome,details=None):
        prior=self.store.all(); previous=prior[-1].event_hash if prior else "0"*64
        body={"sequence":len(prior)+1,"timestamp":datetime.now(timezone.utc).isoformat(),"event":event,"actor":actor,"command_id":command_id,"outcome":outcome,"details":details or {},"previous_hash":previous}
        digest=hashlib.sha256(json.dumps(body,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
        item=AuditEvent(**body,event_hash=digest); self.store.append(item); return item
