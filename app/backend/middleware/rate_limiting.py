"""
Rate limiting middleware for API endpoints
"""

import time
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from collections import defaultdict, deque

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests: Dict[str, deque] = defaultdict(deque)
    
    def is_allowed(self, key: str, limit: int, window_seconds: int) -> Tuple[bool, Dict[str, int]]:
        """
        Check if request is allowed based on rate limit
        Returns (is_allowed, rate_limit_info)
        """
        now = time.time()
        window_start = now - window_seconds
        
        # Clean old requests
        while self.requests[key] and self.requests[key][0] < window_start:
            self.requests[key].popleft()
        
        # Check if under limit
        current_requests = len(self.requests[key])
        is_allowed = current_requests < limit
        
        if is_allowed:
            self.requests[key].append(now)
        
        # Calculate reset time
        reset_time = int(window_start + window_seconds) if self.requests[key] else int(now + window_seconds)
        
        rate_limit_info = {
            'limit': limit,
            'remaining': max(0, limit - current_requests - (1 if is_allowed else 0)),
            'reset': reset_time,
            'retry_after': max(0, int(self.requests[key][0] + window_seconds - now)) if self.requests[key] and not is_allowed else 0
        }
        
        return is_allowed, rate_limit_info

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(limit: int = 100, window: int = 3600):
    """
    Rate limiting decorator
    
    Args:
        limit: Number of requests allowed
        window: Time window in seconds
    """
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            # Use IP address as key (in production, use authenticated user ID)
            client_ip = request.client.host
            key = f"{func.__name__}:{client_ip}"
            
            is_allowed, rate_info = rate_limiter.is_allowed(key, limit, window)
            
            if not is_allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "limit": rate_info['limit'],
                        "retry_after": rate_info['retry_after']
                    },
                    headers={
                        "X-RateLimit-Limit": str(rate_info['limit']),
                        "X-RateLimit-Remaining": str(rate_info['remaining']),
                        "X-RateLimit-Reset": str(rate_info['reset']),
                        "Retry-After": str(rate_info['retry_after'])
                    }
                )
            
            # Add rate limit headers to response
            response = await func(request, *args, **kwargs)
            if hasattr(response, 'headers'):
                response.headers["X-RateLimit-Limit"] = str(rate_info['limit'])
                response.headers["X-RateLimit-Remaining"] = str(rate_info['remaining'])
                response.headers["X-RateLimit-Reset"] = str(rate_info['reset'])
            
            return response
        
        return wrapper
    return decorator