"""Runtime configuration loaded from environment or supplied by tests."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str = "sqlite:///./data/yaotel.sqlite3"
    api_key: str | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            database_url=os.getenv("YAOTEL_DATABASE_URL", cls.database_url),
            api_key=os.getenv("YAOTEL_API_KEY"),
        )
