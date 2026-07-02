
import time
from typing import Dict, Tuple

class RateLimiter:
    """
    Simple in-memory rate limiter.
    """
    def __init__(self, requests_per_minute: int = 60):
        self.limit = requests_per_minute
        self.requests: Dict[str, List[float]] = {}

    def check_rate_limit(self, user_id: str) -> bool:
        """
        Returns True if request is allowed, False if blocked.
        """
        now = time.time()
        
        if user_id not in self.requests:
            self.requests[user_id] = []
            
        # Clean up old requests
        self.requests[user_id] = [t for t in self.requests[user_id] if now - t < 60]
        
        if len(self.requests[user_id]) >= self.limit:
            return False
            
        self.requests[user_id].append(now)
        return True
