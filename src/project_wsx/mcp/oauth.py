import json

from fastapi import APIRouter
from starlette.requests import Request

from project_wsx.core.logging import logger
from project_wsx.core.settings import Settings

settings = Settings()

oauth_router = APIRouter(tags=["OAuth"])


def _base_url(request: Request) -> str:
    return str(request.base_url).rstrip("/")


@oauth_router.get("/.well-known/oauth-protected-resource/mcp")
async def oauth_protected_resource_mcp(request: Request):
    base_url = _base_url(request)
    return {
        "resource": f"{base_url}/mcp",
        "authorization_servers": [base_url],
        "scopes_supported": ["openid", "profile", "email", "read:tasks", "write:tasks"],
        "bearer_methods_supported": ["header"],
    }


@oauth_router.get("/.well-known/oauth-protected-resource")
async def oauth_protected_resource(request: Request):
    base_url = _base_url(request)
    return {
        "resource": f"{base_url}/mcp",
        "authorization_servers": [base_url],
        "scopes_supported": ["openid", "profile", "email", "read:tasks", "write:tasks"],
        "bearer_methods_supported": ["header"],
    }


@oauth_router.get("/.well-known/oauth-authorization-server")
def oauth_authorization_server(request: Request):
    base_url = _base_url(request)
    return {
        "issuer": base_url,
        "authorization_endpoint": f"https://{settings.auth0_domain}/authorize",
        "token_endpoint": f"https://{settings.auth0_domain}/oauth/token",
        "jwks_uri": f"https://{settings.auth0_domain}/.well-known/jwks.json",
        "registration_endpoint": f"{base_url}/oauth/register",
        "scopes_supported": ["openid", "profile", "email", "read:tasks", "write:tasks"],
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "code_challenge_methods_supported": ["S256"],
        "token_endpoint_auth_methods_supported": ["none"],
    }


@oauth_router.get("/.well-known/openid-configuration")
def openid_configuration():
    return {
        "issuer": f"https://{settings.auth0_domain}/",
        "authorization_endpoint": f"https://{settings.auth0_domain}/authorize",
        "token_endpoint": f"https://{settings.auth0_domain}/oauth/token",
        "jwks_uri": f"https://{settings.auth0_domain}/.well-known/jwks.json",
        "scopes_supported": ["openid", "profile", "email", "read:tasks", "write:tasks"],
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "code_challenge_methods_supported": ["S256"],
    }


@oauth_router.post("/oauth/register")
async def oauth_register(request: Request):
    base_url = _base_url(request)

    raw = await request.body()
    try:
        body = json.loads(raw)
    except Exception:
        body = {}

    logger.debug(
        f"OAuth registration request from client: {body.get('client_name', 'unknown')}"
    )
    logger.debug(f"Requested redirect_uris: {body.get('redirect_uris', [])}")

    return {
        "client_id": settings.auth0_client_id,
        "redirect_uris": body.get("redirect_uris", [f"{base_url}/oauth/callback"]),
        "grant_types": ["authorization_code", "refresh_token"],
        "response_types": ["code"],
        "token_endpoint_auth_method": "none",
    }
