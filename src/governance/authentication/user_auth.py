"""Password authentication and opaque rotating sessions; host supplies durable store."""
import hashlib, hmac, secrets, time
from dataclasses import dataclass
from ..errors import AuthorizationDenied
@dataclass(frozen=True)
class UserIdentity:
    user_id: str
    roles: tuple[str,...] = ("user",)
    active: bool = True
class UserAuthenticator:
    def __init__(self,store,iterations=600000):
        if iterations < 300000: raise ValueError("PBKDF2 work factor too low")
        self.store,self.iterations=store,iterations
    def hash_password(self,password):
        if not isinstance(password,str) or len(password)<12: raise ValueError("Password must be at least 12 characters")
        salt=secrets.token_bytes(16)
        digest=hashlib.pbkdf2_hmac("sha256",password.encode(),salt,self.iterations)
        return salt.hex()+"$"+str(self.iterations)+"$"+digest.hex()
    def register(self,user_id,password):
        if not user_id or self.store.get_identity(user_id): raise ValueError("User ID missing or already registered")
        self.store.create_user(user_id,self.hash_password(password))
    def authenticate(self,user_id,password):
        record=self.store.get_password_record(user_id)
        try:
            salt,rounds,expected=record.split("$"); rounds=int(rounds)
            if not 300000<=rounds<=2000000: raise ValueError("Unsafe hash parameters")
            actual=hashlib.pbkdf2_hmac("sha256",password.encode(),bytes.fromhex(salt),rounds).hex()
        except Exception: raise AuthorizationDenied("Invalid credentials") from None
        if not hmac.compare_digest(actual,expected): raise AuthorizationDenied("Invalid credentials")
        identity=self.store.get_identity(user_id)
        if not identity or not identity.active: raise AuthorizationDenied("Account inactive")
        return identity
def new_session_token(): return secrets.token_urlsafe(48)
def hash_session_token(token): return hashlib.sha256(token.encode()).hexdigest()
class SessionManager:
    """Store only token hashes; store.rotate_session must atomically consume old and insert new."""
    def __init__(self,store,ttl_seconds=3600,clock=time.time):
        if not 60<=ttl_seconds<=86400: raise ValueError("Session TTL must be 60..86400 seconds")
        self.store,self.ttl,self.clock=store,ttl_seconds,clock
    def issue(self,user_id):
        token=new_session_token()
        self.store.put_session(hash_session_token(token),user_id,int(self.clock())+self.ttl)
        return token
    def validate(self,token):
        session=self.store.get_session(hash_session_token(token))
        if not session or session["expires_at"]<=int(self.clock()): raise AuthorizationDenied("Session expired or revoked")
        return session["user_id"]
    def rotate(self,token):
        user_id=self.validate(token); old_hash=hash_session_token(token); new_token=new_session_token()
        if not self.store.rotate_session(old_hash,hash_session_token(new_token),user_id,int(self.clock())+self.ttl):
            raise AuthorizationDenied("Session already rotated or revoked")
        return new_token
    def revoke(self,token): self.store.revoke_session(hash_session_token(token))
