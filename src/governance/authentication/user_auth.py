"""Backend authentication primitives. Session persistence is supplied by the host application."""
import hashlib,hmac,secrets
from dataclasses import dataclass
from ..errors import AuthorizationDenied
@dataclass(frozen=True)
class UserIdentity:
    user_id:str
    roles:tuple[str,...]=("user",)
    active:bool=True
class UserAuthenticator:
    def __init__(self,store,iterations=600000):
        if iterations<300000: raise ValueError("PBKDF2 work factor too low")
        self.store,self.iterations=store,iterations
    def hash_password(self,password):
        if len(password)<12: raise ValueError("Password must be at least 12 characters")
        salt=secrets.token_bytes(16)
        digest=hashlib.pbkdf2_hmac("sha256",password.encode(),salt,self.iterations)
        return "$".join((salt.hex(),str(self.iterations),digest.hex()))
    def authenticate(self,user_id,password):
        record=self.store.get_password_record(user_id)
        try:
            salt,rounds,expected=record.split("$")
            actual=hashlib.pbkdf2_hmac("sha256",password.encode(),bytes.fromhex(salt),int(rounds)).hex()
        except Exception: raise AuthorizationDenied("Invalid credentials") from None
        if not hmac.compare_digest(actual,expected): raise AuthorizationDenied("Invalid credentials")
        identity=self.store.get_identity(user_id)
        if not identity or not identity.active: raise AuthorizationDenied("Account inactive")
        return identity
def new_session_token(): return secrets.token_urlsafe(48)
def hash_session_token(token): return hashlib.sha256(token.encode()).hexdigest()
