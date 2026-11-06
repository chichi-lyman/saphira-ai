import base64
from dataclasses import replace
from datetime import datetime, timezone
import pytest

from src.governance.authentication.admin_mfa import AdminMFA, _code
from src.governance.authentication.user_auth import SessionManager, UserAuthenticator
from src.governance.master_control.nonce_store import InMemoryNonceStore
from src.governance.audit.audit_recorder import AuditRecorder, InMemoryAuditStore
from src.governance.audit.audit_integrity import verify_chain
from src.governance.errors import AuthorizationDenied

class AccountStore:
    def __init__(self): self.users={}; self.sessions={}
    def get_identity(self,uid): return self.users.get(uid,{}).get("identity")
    def create_user(self,uid,password_record):
        from src.governance.authentication.user_auth import UserIdentity
        self.users[uid]={"identity":UserIdentity(uid),"password":password_record}
    def get_password_record(self,uid): return self.users[uid]["password"]
    def put_session(self,h,uid,exp): self.sessions[h]={"user_id":uid,"expires_at":exp}
    def get_session(self,h): return self.sessions.get(h)
    def revoke_session(self,h): self.sessions.pop(h,None)
    def rotate_session(self,old,new,uid,exp):
        if old not in self.sessions: return False
        self.sessions.pop(old); self.sessions[new]={"user_id":uid,"expires_at":exp}; return True

def test_password_registration_authentication_and_session_rotation():
    store=AccountStore(); auth=UserAuthenticator(store)
    auth.register("user-1","Correct horse battery staple!")
    assert auth.authenticate("user-1","Correct horse battery staple!").user_id=="user-1"
    with pytest.raises(AuthorizationDenied): auth.authenticate("user-1","wrong password")
    sessions=SessionManager(store,clock=lambda:1000)
    old=sessions.issue("user-1")
    assert sessions.validate(old)=="user-1"
    new=sessions.rotate(old)
    assert sessions.validate(new)=="user-1"
    with pytest.raises(AuthorizationDenied): sessions.validate(old)

def test_totp_rejects_reused_counter():
    secret="JBSWY3DPEHPK3PXP"; now=1_800_000_000; counter=now//30
    class CounterStore:
        def __init__(self): self.used=set()
        def consume_counter(self,admin,c):
            k=(admin,c)
            if k in self.used: return False
            self.used.add(k); return True
    store=CounterStore(); mfa=AdminMFA(lambda _:secret,store,clock=lambda:now)
    code=_code(secret,counter)
    assert mfa.verify("master-id",code)
    with pytest.raises(AuthorizationDenied): mfa.verify("master-id",code)

def test_nonce_store_is_one_time_and_expires():
    store=InMemoryNonceStore(clock=lambda:100)
    assert store.consume("n-1",110)
    assert not store.consume("n-1",110)
    assert not store.consume("n-2",100)

def test_signed_audit_chain_verification_and_tamper_detection():
    class Signer:
        def sign(self,key_id,message): return b"test-signature:"+message
    class Verifier:
        def verify(self,key_id,message,signature):
            if signature!=b"test-signature:"+message: raise ValueError("bad signature")
    store=InMemoryAuditStore()
    recorder=AuditRecorder(store,signer=Signer(),signing_key_id="audit-key",require_signature=True)
    recorder.record(event="ADMIN_COMMAND",actor="master-id",command_id="c1",outcome="ALLOW")
    assert verify_chain(store.all(),Verifier())
    changed=replace(store.all()[0],outcome="TAMPERED")
    assert not verify_chain((changed,),Verifier())
