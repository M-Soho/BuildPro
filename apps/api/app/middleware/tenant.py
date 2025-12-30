from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import uuid


class TenantContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that extracts tenant_id and user_id from JWT claims
    and sets them on request.state for tenant isolation
    """

    async def dispatch(self, request: Request, call_next: Callable):
        # Skip tenant context for public endpoints
        public_paths = ["/", "/health", "/docs", "/redoc", "/openapi.json"]
        if request.url.path in public_paths:
            return await call_next(request)

        # Extract from JWT claims (set by auth middleware)
        # For now, we'll set defaults - auth will be added in next step
        request.state.tenant_id = getattr(request.state, "tenant_id", None)
        request.state.user_id = getattr(request.state, "user_id", None)
        request.state.user_role = getattr(request.state, "user_role", None)

        # Generate request ID for tracing
        request.state.request_id = str(uuid.uuid4())

        response = await call_next(request)
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request.state.request_id
        
        return response
