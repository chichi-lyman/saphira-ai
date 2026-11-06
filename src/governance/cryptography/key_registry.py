"""Trusted public-key registry; production requires a durable audited store."""
from dataclasses import dataclass
from datetime import datetime,timezone
from ..errors import AuthorizationDenied
@dataclass(frozen=True)
class PublicKeyRecord:
    key_id:str
    administrator_id:str
    public_key_pem:bytes
    algorithm:str="Ed25519"
    active:bool=True
    not_before:datetime|None=None
    not_after:datetime|None=None
class KeyRegistry:
    def __init__(self,store=None): self.store=store
    def register(self,record):
        if record.algorithm!="Ed25519" or not record.key_id or not record.administrator_id or not record.public_key_pem:
            raise ValueError("A named Ed25519 public key is required")
        if not self.store: raise RuntimeError("Durable key registry store required")
        if self.store.get(record.key_id): raise ValueError("Key ID already registered")
        self.store.insert(record)
    def get_trusted(self,key_id,admin_id):
        if not self.store: raise AuthorizationDenied("Trusted key registry unavailable")
        r=self.store.get(key_id); now=datetime.now(timezone.utc)
        if not r or not r.active or r.administrator_id!=admin_id or r.algorithm!="Ed25519":
            raise AuthorizationDenied("Untrusted key")
        if (r.not_before and now<r.not_before) or (r.not_after and now>=r.not_after):
            raise AuthorizationDenied("Key outside validity window")
        return r
