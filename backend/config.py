"""Application configuration using pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import json


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "Applify"
    debug: bool = True

    # CORS
    cors_origins: str = '["http://localhost:3000","http://127.0.0.1:5500","null"]'

    def get_cors_origins(self) -> List[str]:
        try:
            return json.loads(self.cors_origins)
        except Exception:
            return ["*"]

    # Database
    database_url: str = "sqlite:///./job_Applify.db"

    # JWT
    secret_key: str = "change_me_to_a_long_random_secret_string_at_least_32_chars"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7 days

    # LLM
    groq_api_key: str = ""
    openai_api_key: str = ""
    llm_model: str = "llama-3.3-70b-versatile"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 4096


settings = Settings()
