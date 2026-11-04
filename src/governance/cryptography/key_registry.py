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
    def __init__(self): self._records={}
    def register(self,record):
        if record.key_id in self._records: raise ValueError("Key ID already registered")
        self._records[record.key_id]=record
    def get_trusted(self,key_id,admin_id):
        r=self._records.get(key_id); now=datetime.now(timezone.utc)
        if not r or not r.active or r.administrator_id!=admin_id: raise AuthorizationDenied("Untrusted key")
        if (r.not_before and now<r.not_before) or (r.not_after and now>=r.not_after): raise AuthorizationDenied("Key outside validity window")
        return r
