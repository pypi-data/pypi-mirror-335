from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class EarthscaleSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="EARTHSCALE_",
        extra="ignore",
    )

    api_url: str = "https://api.earthscale.ai"
    auth_url: str = "https://supabase.earthscale.ai"
    auth_proxy_url: str = "https://supabase-proxy.earthscale.ai"
    auth_anon_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im12a21pYndoYnBsZm11cmphd2xrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA3NDk4MDUsImV4cCI6MjA1NjMyNTgwNX0.6D3ZOkTMo2iSx_aPz0G7yvX0GeL3fV8rpTZo2q6KFTg"  # noqa: E501
    credentials_file: Path = Path().home() / ".earthscale" / "credentials.json"
    email: str | None = None
    password: str | None = None
    use_proxy: bool = False
