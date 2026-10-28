from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Runtime configuration with safe local defaults."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "CIVIA API"
    app_version: str = "0.2.0"
    database_url: str = ""
    cors_origins: str = "http://localhost:5173"
    ai_enabled: bool = False
    gemini_api_key: str | None = None
    rate_limit: int = Field(default=120, ge=0, le=10000)
    rate_window_seconds: int = Field(default=60, ge=1, le=3600)
    max_body_bytes: int = Field(default=65536, ge=1024, le=1048576)
    database_connect_timeout: int = Field(default=5, ge=1, le=60)
    project_root: Path = PROJECT_ROOT

    @property
    def resolved_database_url(self) -> str:
        configured = self.database_url.strip()
        if configured:
            if configured.startswith("postgresql://"):
                return "postgresql+psycopg://" + configured[len("postgresql://") :]
            if configured.startswith("postgres://"):
                return "postgresql+psycopg://" + configured[len("postgres://") :]
            return configured
        database_path = self.project_root / "work" / "civia_api.db"
        database_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{database_path.as_posix()}"

    @property
    def cors_origin_list(self) -> list[str]:
        origins = [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
        if not origins or "*" in origins:
            raise ValueError("CORS_ORIGINS debe enumerar origenes explicitos")
        return origins

    @property
    def generative_ai_available(self) -> bool:
        # G2 only ships the deterministic fallback. No client or SDK receives a key.
        return False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
