from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class MaxBodySizeMiddleware(BaseHTTPMiddleware):
    """
    Explicitly configures FastAPI to handle massive webhook payloads (Issue #42)
    while protecting other routes from memory-exhaustion DoS attacks.
    """
    def __init__(self, app, global_limit: int = 2 * 1024 * 1024):
        super().__init__(app)
        self.global_limit = global_limit
        # Shopify Webhooks can be massive for huge eCommerce orders.
        self.webhook_limit = 50 * 1024 * 1024  # 50 MB
        
    async def dispatch(self, request: Request, call_next):
        # 1. Determine the path limit
        if request.url.path.startswith("/api/v1/payments") or request.url.path.startswith("/shopify"):
            content_limit = self.webhook_limit
        else:
            content_limit = self.global_limit
            
        # 2. Check the Content-Length header first (Fast fail)
        content_length_str = request.headers.get("content-length")
        if content_length_str:
            try:
                content_length = int(content_length_str)
                if content_length > content_limit:
                    logger.error(f"🚨 Payload too large for {request.url.path}: {content_length} bytes")
                    return JSONResponse(
                        status_code=413,
                        content={"detail": "Request Entity Too Large. Payload exceeds configured bounds."}
                    )
            except ValueError:
                pass
                
        # 3. Stream the body to enforce limits if Content-Length is missing or spoofed
        body_bytes = b""
        async for chunk in request.stream():
            body_bytes += chunk
            if len(body_bytes) > content_limit:
                logger.error(f"🚨 Streamed payload too large for {request.url.path}")
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Request Entity Too Large. Stream exceeded configured bounds."}
                )
                
        # Inject the fully consumed body back into the request so downstream routes can read it
        async def receive_injected():
            return {"type": "http.request", "body": body_bytes, "more_body": False}
        request._receive = receive_injected

        response = await call_next(request)
        return response
