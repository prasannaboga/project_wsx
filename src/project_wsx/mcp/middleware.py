from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from project_wsx.core.settings import Settings

settings = Settings()


class AuthHeaderMiddleware(BaseHTTPMiddleware):
    """Adds WWW-Authenticate header to 401 responses for OAuth discovery."""

    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        response = await call_next(request)

        if response.status_code == 401:
            base_url = str(request.base_url).rstrip("/")
            response.headers["WWW-Authenticate"] = (
                'Bearer realm="OAuth", '
                'error="invalid_token", '
                'error_description="Authentication required", '
                f'resource_metadata="{base_url}/.well-known/oauth-protected-resource/mcp"'
            )

        return response


class MCPPathMiddleware(BaseHTTPMiddleware):
    """Rewrites /mcp to /mcp/ internally — avoids 307 redirects to clients."""

    async def dispatch(self, request: Request, call_next):
        if request.scope["path"] == "/mcp":
            request.scope["path"] = "/mcp/"
            request.scope["raw_path"] = b"/mcp/"
        return await call_next(request)
