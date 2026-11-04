PERMISSIONS=frozenset({
 "profile:read","profile:write","feature:use","resource:read","resource:write",
 "agent:execute","agent:inspect","agent:stop","agent:suspend","agent:revoke",
 "task:cancel","policy:change","recovery:approve","system_state:modify",
 "service:restore","audit:read","keys:rotate","emergency:stop"
})
PRIVILEGED=frozenset({
 "agent:stop","agent:suspend","agent:revoke","task:cancel","policy:change",
 "recovery:approve","system_state:modify","service:restore","keys:rotate","emergency:stop"
})
# Privilege is derived from the signed command's semantics, never from a caller-supplied role.
COMMAND_PERMISSIONS={
 ("AGENT_OVERRIDE","STOP_AGENT"):"agent:stop",
 ("AGENT_OVERRIDE","CANCEL_EXECUTION"):"task:cancel",
 ("AGENT_OVERRIDE","SUSPEND_AGENT"):"agent:suspend",
 ("AGENT_OVERRIDE","REVOKE_AGENT_PERMISSIONS"):"agent:revoke",
 ("GOVERNANCE_OVERRIDE","CHANGE_POLICY"):"policy:change",
 ("RECOVERY_OVERRIDE","APPROVE_RECOVERY"):"recovery:approve",
 ("SYSTEM_OVERRIDE","MODIFY_PROTECTED_STATE"):"system_state:modify",
 ("SERVICE_OVERRIDE","RESTORE_SERVICE"):"service:restore",
 ("KEY_ADMIN","ROTATE_MASTER_KEY"):"keys:rotate",
 ("EMERGENCY_STOP","ENGAGE"):"emergency:stop",
 ("EMERGENCY_STOP","RELEASE"):"emergency:stop",
}
def is_known(permission): return permission in PERMISSIONS
def is_privileged(permission): return permission in PRIVILEGED
def permission_for_command(command,action): return COMMAND_PERMISSIONS.get((command,action))
