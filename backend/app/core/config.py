from pydantic_settings import BaseSettings
from typing import List, Union
import json


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # App
    APP_NAME: str = "Product Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # CORS — handled manually to support both string and list formats
    ALLOWED_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000"
    ]

    def get_allowed_origins(self) -> List[str]:
        """
        Safely parse ALLOWED_ORIGINS regardless of how it was set.
        Handles:
          - Plain string: "https://example.com"
          - JSON array:   ["https://example.com"]
          - Python list:  already a list
          - Comma separated: "https://a.com,https://b.com"
        """
        if isinstance(self.ALLOWED_ORIGINS, list):
            return self.ALLOWED_ORIGINS

        value = self.ALLOWED_ORIGINS.strip()

        # Try JSON parse first
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
            return [str(parsed)]
        except (json.JSONDecodeError, ValueError):
            pass

        # Try comma separated
        if "," in value:
            return [url.strip() for url in value.split(",")]

        # Plain single URL
        return [value]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


settings = Settings()