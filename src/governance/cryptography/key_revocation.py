from datetime import datetime,timezone
class KeyRevocationRegistry:
    def __init__(self): self._revoked={}
    def revoke(self,key_id,reason): self._revoked[key_id]=(datetime.now(timezone.utc),reason)
    def is_revoked(self,key_id): return key_id in self._revoked
    def reason(self,key_id): return self._revoked.get(key_id)
