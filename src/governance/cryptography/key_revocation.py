"""Durable key revocation; revocation records are retained for audit."""
from datetime import datetime,timezone
from ..errors import AuthorizationDenied
class KeyRevocationRegistry:
    def __init__(self,store=None): self.store=store
    def revoke(self,key_id,reason,*,actor_id):
        if not self.store or not key_id or not reason or not actor_id:
            raise AuthorizationDenied("Audited revocation store and actor required")
        self.store.revoke_once(key_id,{"revoked_at":datetime.now(timezone.utc).isoformat(),"reason":reason,"actor_id":actor_id})
    def is_revoked(self,key_id):
        if not self.store: raise AuthorizationDenied("Revocation registry unavailable")
        return self.store.is_revoked(key_id)
    def reason(self,key_id):
        if not self.store: raise AuthorizationDenied("Revocation registry unavailable")
        return self.store.get_revocation(key_id)
