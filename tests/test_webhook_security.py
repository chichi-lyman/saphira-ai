from src.integrations.webhook_security import WebhookSignatureVerifier


def test_webhook_valid_signature_and_replay_protection():
    verifier = WebhookSignatureVerifier("s" * 40)
    body, timestamp = b'{"event":"order.created"}', 1000
    signature = verifier.signature(timestamp, body)
    assert verifier.verify(timestamp, body, signature, "evt-1", now=1000)
    assert not verifier.verify(timestamp, body, signature, "evt-1", now=1000)


def test_webhook_rejects_stale_or_tampered_payload():
    verifier = WebhookSignatureVerifier("s" * 40)
    body, timestamp = b'{"event":"order.created"}', 1000
    signature = verifier.signature(timestamp, body)
    assert not verifier.verify(timestamp, body, signature, "evt-old", now=2000)
    assert not verifier.verify(timestamp, body + b" ", signature, "evt-tampered", now=1000)
