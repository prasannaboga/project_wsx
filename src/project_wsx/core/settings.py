from pydantic import computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./development_wsx.sqlite"
    environment: str = "development"

    auth0_domain: str | None = None
    auth0_audience: str | None = None
    auth0_client_id: str | None = None
    auth0_client_secret: str | None = None
    mcp_resource_url: str | None = None

    # MCP 
    mcp_debug: bool = True
    mcp_log_level: str = "DEBUG"

    # CORS
    cors_origins_str: str = "http://localhost:6274"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_str.split(",")]
