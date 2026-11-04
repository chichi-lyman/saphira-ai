"""RFC 6238 TOTP MFA with atomic replay-counter protection."""
import base64,hashlib,hmac,struct,time
from ..errors import AuthorizationDenied
def _code(secret_b32,counter):
    key=base64.b32decode(secret_b32.upper()+"="*((8-len(secret_b32)%8)%8))
    digest=hmac.new(key,struct.pack(">Q",counter),hashlib.sha1).digest()
    offset=digest[-1]&15
    value=(struct.unpack(">I",digest[offset:offset+4])[0]&0x7fffffff)%1000000
    return "%06d"%value
def verify_totp(secret_b32,code,at=None,window=1):
    if not isinstance(code,str) or not code.isdigit() or len(code)!=6: return False
    try:
        counter=int(time.time() if at is None else at)//30
        return any(hmac.compare_digest(_code(secret_b32,counter+offset),code) for offset in range(-window,window+1))
    except Exception: return False
class AdminMFA:
    """counter_store.consume_counter(admin_id,counter) must be atomic and persistent."""
    def __init__(self,secret_resolver,counter_store,clock=time.time):
        self.secret_resolver,self.counter_store,self.clock=secret_resolver,counter_store,clock
    def verify(self,admin_id,code):
        secret=self.secret_resolver(admin_id)
        if not secret or not isinstance(code,str) or not code.isdigit() or len(code)!=6:
            raise AuthorizationDenied("Administrator MFA failed")
        current=int(self.clock())//30; matched=None
        for offset in (-1,0,1):
            candidate=current+offset
            try:
                if hmac.compare_digest(_code(secret,candidate),code): matched=candidate; break
            except Exception: break
        if matched is None or not self.counter_store.consume_counter(admin_id,matched):
            raise AuthorizationDenied("Administrator MFA invalid or already used")
        return True
