from dataclasses import dataclass,field
from .permission_registry import is_known
from ..errors import AuthorizationDenied
DEFAULT_ROLE_PERMISSIONS={"user":{"profile:read","profile:write","feature:use","resource:read","resource:write"},"premium":{"profile:read","profile:write","feature:use","resource:read","resource:write"},"agent":{"agent:execute","resource:read"},"operator":{"agent:inspect","service:restore","audit:read"},"master_admin":set()}
@dataclass(frozen=True)
class Principal:
    subject_id:str
    kind:str
    roles:tuple[str,...]=()
    scopes:frozenset[str]=field(default_factory=frozenset)
    active:bool=True
class RBAC:
    def __init__(self,role_permissions=None): self.roles=role_permissions or DEFAULT_ROLE_PERMISSIONS
    def allows(self,p,permission,resource=None):
        if not p.active or not is_known(permission): return False
        grants=set().union(*(self.roles.get(r,set()) for r in p.roles))
        return permission in grants and (resource is None or "*" in p.scopes or resource in p.scopes)
    def require(self,p,permission,resource=None):
        if not self.allows(p,permission,resource): raise AuthorizationDenied("Permission denied: "+permission)
