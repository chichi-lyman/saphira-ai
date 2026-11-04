PERMISSIONS=frozenset({"profile:read","profile:write","feature:use","resource:read","resource:write","agent:execute","agent:inspect","agent:stop","agent:suspend","agent:revoke","task:cancel","policy:change","recovery:approve","system_state:modify","service:restore","audit:read","keys:rotate","emergency:stop"})
PRIVILEGED=frozenset({"agent:stop","agent:suspend","agent:revoke","task:cancel","policy:change","recovery:approve","system_state:modify","service:restore","keys:rotate","emergency:stop"})
def is_known(permission): return permission in PERMISSIONS
def is_privileged(permission): return permission in PRIVILEGED
