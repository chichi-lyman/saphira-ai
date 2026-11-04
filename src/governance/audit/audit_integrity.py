import hashlib,json
from dataclasses import asdict
def verify_chain(events):
    previous="0"*64
    for sequence,event in enumerate(events,1):
        data=asdict(event); digest=data.pop("event_hash")
        if data["sequence"]!=sequence or data["previous_hash"]!=previous: return False
        calculated=hashlib.sha256(json.dumps(data,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
        if calculated!=digest: return False
        previous=digest
    return True
