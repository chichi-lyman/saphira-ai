"""Verify audit hash chain and, when configured, KMS signatures."""
import base64,hashlib,json
from dataclasses import asdict
def verify_chain(events,signature_verifier=None):
    previous="0"*64
    for sequence,event in enumerate(events,1):
        data=asdict(event); digest=data.pop("event_hash")
        signing_key_id=data.pop("signing_key_id",None); signature=data.pop("signature",None)
        if data["sequence"]!=sequence or data["previous_hash"]!=previous: return False
        calculated=hashlib.sha256(json.dumps(data,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
        if calculated!=digest: return False
        if signature is not None:
            if signature_verifier is None or not signing_key_id: return False
            try: signature_verifier.verify(signing_key_id,bytes.fromhex(digest),base64.b64decode(signature,validate=True))
            except Exception: return False
        previous=digest
    return True
