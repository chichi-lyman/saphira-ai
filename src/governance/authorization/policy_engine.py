from dataclasses import dataclass
from enum import Enum
from .permission_registry import is_privileged
from .rbac import RBAC
from ..errors import AuthorizationDenied
class Decision(str,Enum): ALLOW="ALLOW"; REQUIRE_APPROVAL="REQUIRE_APPROVAL"; DENY="DENY"
@dataclass(frozen=True)
class PolicyDecision:
    decision:Decision
    reason:str
    permission:str
class PolicyEngine:
    def __init__(self,rbac=None): self.rbac=rbac or RBAC()
    def evaluate(self,principal,permission,resource=None):
        if is_privileged(permission): return PolicyDecision(Decision.REQUIRE_APPROVAL,"Master signature required",permission)
        if self.rbac.allows(principal,permission,resource): return PolicyDecision(Decision.ALLOW,"Role and scope allow",permission)
        return PolicyDecision(Decision.DENY,"No matching grant",permission)
    def require_standard(self,principal,permission,resource=None):
        result=self.evaluate(principal,permission,resource)
        if result.decision!=Decision.ALLOW: raise AuthorizationDenied(result.reason)
