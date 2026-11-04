from dataclasses import dataclass
from datetime import datetime,timezone
import secrets
from ..errors import AuthorizationDenied
@dataclass(frozen=True)
class DelegatedGrant:
    token:str; agent_id:str; task_id:str; permissions:frozenset[str]; expires_at:int
class DelegatedCredentialIssuer:
    def __init__(self,store,max_ttl_seconds=900): self.store=store; self.max_ttl=max_ttl_seconds
    def issue(self,*,agent_id,task_id,permissions,ttl_seconds,approved):
        if not approved: raise AuthorizationDenied("Governance approval required")
        if not agent_id or not task_id or not 1<=ttl_seconds<=self.max_ttl: raise ValueError("Invalid grant parameters")
        grant=DelegatedGrant(secrets.token_urlsafe(40),agent_id,task_id,frozenset(permissions),int(datetime.now(timezone.utc).timestamp())+ttl_seconds)
        self.store.put(grant); return grant
    def validate(self,token,*,agent_id,task_id,permission):
        grant=self.store.get(token)
        return bool(grant and grant.agent_id==agent_id and grant.task_id==task_id and permission in grant.permissions and grant.expires_at>int(datetime.now(timezone.utc).timestamp()) and not self.store.is_revoked(token))
