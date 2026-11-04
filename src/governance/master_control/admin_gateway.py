"""Fail-closed master command authorization gateway."""
import base64,time
from ..errors import AuthorizationDenied,ReplayDetected
from ..cryptography.signature_verifier import Ed25519Verifier
class AdminGateway:
    def __init__(self,*,master_admin_id,key_registry,revocations,nonce_store,mfa,verifier=None,clock=time.time,max_ttl_seconds=300):
        if not master_admin_id: raise ValueError("Pinned master administrator ID required")
        self.master=master_admin_id; self.keys=key_registry; self.revocations=revocations; self.nonces=nonce_store
        self.mfa=mfa; self.verifier=verifier or Ed25519Verifier(); self.clock=clock; self.max_ttl=max_ttl_seconds
    def authorize(self,envelope,*,mfa_code,required_scope):
        if envelope.administrator_id!=self.master: raise AuthorizationDenied("Not designated master administrator")
        self.mfa.verify(self.master,mfa_code); now=int(self.clock())
        if (envelope.expires_at<=now or envelope.issued_at>now+30 or envelope.issued_at>now
            or envelope.expires_at-envelope.issued_at>self.max_ttl):
            raise AuthorizationDenied("Invalid command time window")
        if not envelope.command_id or not envelope.nonce or envelope.scope!=required_scope:
            raise AuthorizationDenied("Command identity or scope mismatch")
        if self.revocations.is_revoked(envelope.key_id): raise AuthorizationDenied("Signing key revoked")
        key=self.keys.get_trusted(envelope.key_id,self.master)
        if envelope.algorithm!="Ed25519" or key.algorithm!=envelope.algorithm:
            raise AuthorizationDenied("Unsupported signature algorithm")
        try: signature=base64.b64decode(envelope.signature,validate=True)
        except Exception: raise AuthorizationDenied("Malformed signature") from None
        self.verifier.verify(key.public_key_pem,envelope.canonical_bytes(),signature)
        if not self.nonces.consume(envelope.nonce,envelope.expires_at): raise ReplayDetected("Nonce already consumed")
        return envelope.command_id
