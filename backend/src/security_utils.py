"""Security utilities - JWT validation, sanitization, rate limiting"""
import os
from functools import wraps
from datetime import datetime, timedelta
from typing import Callable, Any

def validate_jwt_secret() -> str:
    """Validate JWT secret from environment"""
    secret = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
    if len(secret) < 10 and "production" in os.getenv("ENVIRONMENT", "dev"):
        raise ValueError("JWT_SECRET must be at least 10 characters in production")
    return secret

def sanitize_log(text: str) -> str:
    """Remove sensitive information from logs"""
    sensitive_patterns = ["password", "token", "secret", "key", "api_key"]
    result = text
    for pattern in sensitive_patterns:
        result = result.replace(pattern, "***")
    return result

class RateLimiter:
    """Simple in-memory rate limiter"""
    def __init__(self):
        self.requests = {}
    
    def is_limited(self, key: str, max_requests: int = 100, window_seconds: int = 60) -> bool:
        """Check if request should be rate limited"""
        now = datetime.now()
        if key not in self.requests:
            self.requests[key] = []
        
        # Clean old requests outside window
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if (now - req_time).total_seconds() < window_seconds
        ]
        
        if len(self.requests[key]) >= max_requests:
            return True
        
        self.requests[key].append(now)
        return False

# Global rate limiter instance
rate_limiter = RateLimiter()
