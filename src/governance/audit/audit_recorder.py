"""Hash-chained, optionally KMS-signed audit events.

Production must set require_signature=True and supply a KMS-backed signer whose
sign(key_id, message) method never exports private key material. The backing store
must provide atomic append_if_head and enforce append-only retention/backups.
"""
from dataclasses import dataclass
from datetime import datetime,timezone
import base64,hashlib,json
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
    signing_key_id:str|None=None
    signature:str|None=None
class InMemoryAuditStore:
    """Test-only. Not durable, independently backed up, or tamper-proof."""
    def __init__(self): self.events=[]; self.lock=Lock()
    def all(self):
        with self.lock: return tuple(self.events)
    def append_if_head(self,event,expected_previous_hash):
        with self.lock:
            current=self.events[-1].event_hash if self.events else "0"*64
            if current!=expected_previous_hash: return False
            self.events.append(event); return True
class AuditRecorder:
    def __init__(self,store,*,signer=None,signing_key_id=None,require_signature=False):
        if require_signature and (not signer or not signing_key_id):
            raise ValueError("Production audit signing requires a KMS signer and key ID")
        self.store,self.signer,self.signing_key_id=store,signer,signing_key_id
        self.require_signature=require_signature
    def record(self,*,event,actor,command_id,outcome,details=None):
        prior=self.store.all(); previous=prior[-1].event_hash if prior else "0"*64
        body={"sequence":len(prior)+1,"timestamp":datetime.now(timezone.utc).isoformat(),
              "event":event,"actor":actor,"command_id":command_id,"outcome":outcome,
              "details":details or {},"previous_hash":previous}
        canonical=json.dumps(body,sort_keys=True,separators=(",",":"),default=str).encode()
        digest=hashlib.sha256(canonical).hexdigest()
        signature=None
        if self.signer:
            signature=base64.b64encode(self.signer.sign(self.signing_key_id,bytes.fromhex(digest))).decode()
        elif self.require_signature:
            raise RuntimeError("Audit signature unavailable")
        item=AuditEvent(**body,event_hash=digest,signing_key_id=self.signing_key_id,signature=signature)
        if not self.store.append_if_head(item,previous):
            raise RuntimeError("Audit append conflict; reload chain head before retry")
        return item
