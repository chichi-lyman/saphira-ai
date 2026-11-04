from dataclasses import dataclass,asdict
from datetime import datetime,timezone
import hashlib,json,secrets,base64
@dataclass(frozen=True)
class SignedCommand:
    command_id:str
    administrator_id:str
    key_id:str
    command:str
    target:str
    action:str
    scope:str
    issued_at:int
    expires_at:int
    nonce:str
    signature:str
    algorithm:str="Ed25519"
    def payload(self):
        data=asdict(self); data.pop("signature"); return data
    def canonical_bytes(self): return json.dumps(self.payload(),sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    @property
    def digest(self): return hashlib.sha256(self.canonical_bytes()).hexdigest()
class CommandFactory:
    def __init__(self,kms_signer): self.signer=kms_signer
    def create(self,*,administrator_id,key_id,command,target,action,scope,ttl_seconds=120):
        if not 1<=ttl_seconds<=300: raise ValueError("TTL must be 1..300 seconds")
        now=int(datetime.now(timezone.utc).timestamp())
        cmd=SignedCommand(secrets.token_urlsafe(18),administrator_id,key_id,command,target,action,scope,now,now+ttl_seconds,secrets.token_urlsafe(24),"")
        signature=base64.b64encode(self.signer.sign(key_id,cmd.canonical_bytes())).decode()
        return SignedCommand(**{**cmd.payload(),"signature":signature})
