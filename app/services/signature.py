import hmac
import hashlib


def generate_signature(api_key: str, token: str, timestamp: str) -> str:
    """Generate HMAC-SHA1 signature for API requests"""
    return hmac.new(
        key=api_key.encode(encoding="UTF-8"),
        msg=f"{timestamp}{token}".encode(encoding="UTF-8"),
        digestmod=hashlib.sha1,
    ).hexdigest()


def verify_signature(api_key: str, token: str, timestamp: str, signature: str) -> bool:
    """Verify HMAC signature for API requests"""
    hmac_digest = generate_signature(api_key, token, timestamp)
    return hmac.compare_digest(signature, hmac_digest)
