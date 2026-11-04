"""RFC 6238 TOTP administrator step-up authentication."""
import base64,hashlib,hmac,struct,time
from ..errors import AuthorizationDenied
def verify_totp(secret_b32,code,at=None,window=1):
    if not code.isdigit() or len(code)!=6: return False
    try: key=base64.b32decode(secret_b32.upper()+"="*((8-len(secret_b32)%8)%8))
    except Exception: return False
    now=int(time.time() if at is None else at)
    for offset in range(-window,window+1):
        digest=hmac.new(key,struct.pack(">Q",now//30+offset),hashlib.sha1).digest(); i=digest[-1]&15
        value=(struct.unpack(">I",digest[i:i+4])[0]&0x7fffffff)%1000000
        if hmac.compare_digest("%06d"%value,code): return True
    return False
class AdminMFA:
    def __init__(self,secret_resolver): self.secret_resolver=secret_resolver
    def verify(self,admin_id,code):
        secret=self.secret_resolver(admin_id)
        if not secret or not verify_totp(secret,code): raise AuthorizationDenied("Administrator MFA failed")
