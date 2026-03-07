from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./development_wsx.sqlite"
    environment: str = "development"

    auth0_domain: str | None = None
    auth0_audience: str | None = None
    resource_server_url: str | None = None


    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
