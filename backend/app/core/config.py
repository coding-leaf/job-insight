from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "JobInsight API"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "job_insight"
    # When False, the backend strictly requires MongoDB as the primary datastore
    # and will not silently fall back to local JSON memory storage.
    ENABLE_JSON_FALLBACK: bool = False

    # CORS settings
    CORS_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=(
            str(Path(__file__).resolve().parents[2] / ".env"),
            str(Path(__file__).resolve().parents[3] / ".env"),
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
