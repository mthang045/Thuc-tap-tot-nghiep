import hashlib
import hmac
from urllib.parse import urlencode


def _normalize_params(params):
    """Return a stable string map for VNPay signing and URL building."""
    normalized = {
        str(key): str(value)
        for key, value in params.items()
        if value is not None and value != ''
    }
    return dict(sorted(normalized.items(), key=lambda item: item[0]))


def _build_hash_data(params):
    """Build URL-encoded hashdata string for HMAC signing (VNPay requirement)."""
    return urlencode(list(params.items()))


def _build_query_string(params):
    """Build URL-encoded query string for redirect URL."""
    return urlencode(list(params.items()))


def create_payment_url(base_url, params, hash_secret):
    """Create signed VNPay payment URL from params."""
    normalized = _normalize_params(params)
    hash_data = _build_hash_data(normalized)
    query = _build_query_string(normalized)
    signature = hmac.new(
        hash_secret.encode('utf-8'),
        hash_data.encode('utf-8'),
        hashlib.sha512,
    ).hexdigest()
    return (
        f"{base_url}?{query}&vnp_SecureHashType=HMACSHA512&vnp_SecureHash={signature}",
        signature,
    )


def verify_return_signature(return_params, hash_secret):
    """Verify VNPay callback signature."""
    secure_hash = return_params.get('vnp_SecureHash', '')
    if not secure_hash:
        return False

    raw_params = _normalize_params(
        {
            key: value
            for key, value in return_params.items()
            if key.startswith('vnp_') and key not in {'vnp_SecureHash', 'vnp_SecureHashType'}
        }
    )
    hash_data = _build_hash_data(raw_params)
    expected = hmac.new(
        hash_secret.encode('utf-8'),
        hash_data.encode('utf-8'),
        hashlib.sha512,
    ).hexdigest()
    return expected.lower() == secure_hash.lower()
