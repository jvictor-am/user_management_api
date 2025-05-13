import time
from typing import Dict, Tuple

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        requests_limit: int = 10,
        window_size: int = 60
    ):
        super().__init__(app)
        self.requests_limit = requests_limit
        self.window_size = window_size
        self.request_counts: Dict[str, Tuple[int, float]] = {}

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host
        current_time = time.time()
        
        # Clean old entries
        for key in list(self.request_counts.keys()):
            count, timestamp = self.request_counts[key]
            if current_time - timestamp > self.window_size:
                del self.request_counts[key]
        
        # Check rate limit
        if ip in self.request_counts:
            count, timestamp = self.request_counts[ip]
            if count >= self.requests_limit:
                return Response(
                    content="Rate limit exceeded",
                    status_code=429
                )
            self.request_counts[ip] = (count + 1, timestamp)
        else:
            self.request_counts[ip] = (1, current_time)
        
        response = await call_next(request)
        return response
