"""Controlled master public-key rotation.

The supplied store must implement atomic_rotate(old_key_id, new_record, revoked_record).
The operation must be called only after the AdminGateway has verified a dedicated
keys:rotate command and the administrator has completed the recovery policy checks.
"""
from ..errors import AuthorizationDenied
class KeyRotationService:
    def __init__(self,key_store,revocation_store,audit):
        self.key_store,self.revocations,self.audit=key_store,revocation_store,audit
    def rotate(self,*,old_key_id,new_record,authorized_by,authorization_command_id):
        if not all((old_key_id,new_record,authorized_by,authorization_command_id)):
            raise AuthorizationDenied("Key rotation requires verified authorization context")
        if new_record.key_id==old_key_id or new_record.administrator_id!=authorized_by:
            raise AuthorizationDenied("Replacement key identity mismatch")
        # Atomic store operation must install the new public key and retire the old key together.
        if not self.key_store.atomic_rotate(old_key_id,new_record):
            raise AuthorizationDenied("Key rotation precondition failed")
        self.revocations.revoke(old_key_id,"superseded by "+new_record.key_id,actor_id=authorized_by)
        self.audit.record(event="MASTER_KEY_ROTATED",actor=authorized_by,
                          command_id=authorization_command_id,outcome="APPLIED",
                          details={"old_key_id":old_key_id,"new_key_id":new_record.key_id})
        return new_record.key_id
