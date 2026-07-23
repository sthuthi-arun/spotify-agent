import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_version: str
    database_path: str
    log_level: str


def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv(
            "APP_NAME",
            "Spotify Data Agent",
        ),
        app_version=os.getenv(
            "APP_VERSION",
            "1.0.0",
        ),
        database_path=os.getenv(
            "DATABASE_PATH",
            "data/spotify.duckdb",
        ),
        log_level=os.getenv(
            "LOG_LEVEL",
            "INFO",
        ),
    )


settings = get_settings()
