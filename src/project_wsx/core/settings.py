from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./development_wsx.sqlite"
    environment: str = "development"

    mcp_auth_enabled: bool = False
    oauth_issuer_url: str | None = None
    oauth_client_id: str | None = None
    oauth_client_secret: str | None = None
    oauth_grant_type: str | None = None
    oauth_required_scopes: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @computed_field
    @property
    def oauth_access_token_url(self) -> str:
        return f"{self.oauth_issuer_url}/oauth/token"
    
    @computed_field
    @property
    def oauth_refresh_token_url(self) -> str:
        return f"{self.oauth_issuer_url}/oauth/token/refresh"

    @computed_field
    @property
    def oauth_token_info_url(self) -> str:
        return f"{self.oauth_issuer_url}/oauth/token/info"

    @computed_field
    @property
    def oauth_introspection_url(self) -> str:
        return f"{self.oauth_issuer_url}/oauth/introspect"
