from ..errors import AuthorizationDenied,ConfigurationError
class Ed25519Verifier:
    def verify(self,pem,message,signature):
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
            key=serialization.load_pem_public_key(pem)
            if not isinstance(key,Ed25519PublicKey): raise AuthorizationDenied("Wrong public-key type")
            key.verify(signature,message)
        except ImportError as exc: raise ConfigurationError("cryptography package is required") from exc
        except AuthorizationDenied: raise
        except Exception as exc: raise AuthorizationDenied("Invalid signature") from exc
