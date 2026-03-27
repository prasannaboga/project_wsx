import jwt
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP
from pydantic import AnyHttpUrl

from project_wsx.core.logging import logger
from project_wsx.core.settings import Settings

settings = Settings()

auth_settings = AuthSettings(
    issuer_url=AnyHttpUrl(f"https://{settings.auth0_domain}/"),
    resource_server_url=AnyHttpUrl("http://localhost:8101/mcp"),
    required_scopes=["read:tasks", "write:tasks", "openid", "profile", "email"],
)


class Auth0TokenVerifier(TokenVerifier):
    def __init__(self):
        self.domain = settings.auth0_domain
        self.audience = settings.auth0_audience
        self.jwks_url = f"https://{settings.auth0_domain}/.well-known/jwks.json"
        self.issuer = f"https://{settings.auth0_domain}/"
        self.jwks_client = jwt.PyJWKClient(self.jwks_url)

    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self.audience,
                issuer=self.issuer,
            )

            return AccessToken(
                token=token,
                client_id=payload.get("sub", ""),
                scopes=payload.get("scope", "").split(),
                expires_at=payload.get("exp"),
                issued_at=payload.get("iat"),
            )
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None


token_verifier = Auth0TokenVerifier()


def create_mcp():
    mcp = FastMCP(
        "project_wsx_mcp_server",
        debug=settings.mcp_debug,
        json_response=True,
        log_level=settings.mcp_log_level,
        stateless_http=True,
        streamable_http_path="/",
        auth=auth_settings,
        token_verifier=token_verifier,
    )

    return mcp
