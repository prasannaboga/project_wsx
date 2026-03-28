from project_wsx.core.logging import logger, setup_logging

setup_logging()  # noqa: E402 — must run before other imports trigger logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from project_wsx.api import api_router
from project_wsx.core.database import init_db
from project_wsx.core.settings import Settings
from project_wsx.mcp.registry import register_all
from project_wsx.mcp.server import create_mcp

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class MCPPathMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.scope["path"] == "/mcp":
            request.scope["path"] = "/mcp/"
            request.scope["raw_path"] = b"/mcp/"

        return await call_next(request)


class AuthHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if response.status_code == 401:
            response.headers["WWW-Authenticate"] = (
                'Bearer realm="OAuth", '
                'error="invalid_token", '
                'error_description="Authentication required", '
                'resource_metadata="http://localhost:8101/.well-known/oauth-protected-resource/mcp"'
            )
        return response


settings = Settings()
logger.debug(f"Loaded settings: {settings.model_dump()}")
mcp = create_mcp()
register_all(mcp)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("Initializing database...")
    init_db()
    async with mcp.session_manager.run():
        logger.debug("MCP server is running...")
        yield

    logger.debug("Shutting down...")


app = FastAPI(
    title="Project WSX API",
    description="API for Project WSX",
    version="0.1.2",
    lifespan=lifespan,
)


app.add_middleware(AuthHeaderMiddleware)
app.add_middleware(MCPPathMiddleware)


@app.get("/")
def index():
    return {"Hello": "World"}


@app.get("/health")
def health():
    return {"status": "ok", "environment": settings.environment}


@app.get("/.well-known/oauth-authorization-server")
def oauth_authorization_server(request: Request):
    base_url = str(request.base_url).rstrip("/")
    data = {
        "issuer": base_url,
        "authorization_endpoint": f"https://{settings.auth0_domain}/authorize",
        "token_endpoint": f"https://{settings.auth0_domain}/oauth/token",
        "jwks_uri": f"https://{settings.auth0_domain}/.well-known/jwks.json",
        "registration_endpoint": f"{base_url}/oauth/register",
        "scopes_supported": ["openid", "profile", "email", "read:tasks", "write:tasks"],
        "response_types_supported": ["code"],
        "grant_types_supported": [
            "authorization_code",
            "refresh_token",
        ],
        "code_challenge_methods_supported": ["S256"],
        "token_endpoint_auth_methods_supported": [
            "client_secret_basic",
            "client_secret_post",
        ],
    }
    return data


@app.get("/.well-known/oauth-protected-resource/mcp")
async def oauth_protected_resource(request: Request):
    base_url = str(request.base_url).rstrip("/")

    return {
        "resource": f"{base_url}/mcp",
        "authorization_servers": [base_url],
        "scopes_supported": ["openid", "profile", "email", "read:tasks", "write:tasks"],
        "bearer_methods_supported": ["header"],
    }


@app.post("/oauth/register")
async def oauth_register(request: Request):
    base_url = str(request.base_url).rstrip("/")
    return {
        "client_id": settings.auth0_client_id,
        "client_secret": settings.auth0_client_secret,
        "redirect_uris": [
            "https://oauth.pstmn.io/v1/callback",
            f"{base_url}/callback",
            "https://vscode.dev/redirect",
            "cursor://anysphere.cursor-mcp/oauth/callback"
        ],
        "grant_types": ["authorization_code", "refresh_token"],
        "response_types": ["code"],
        "token_endpoint_auth_method": "client_secret_post",
    }


app.include_router(api_router, prefix="/api")
app.router.redirect_slashes = False
app.mount("/mcp", mcp.streamable_http_app(), name="MCP Server")
