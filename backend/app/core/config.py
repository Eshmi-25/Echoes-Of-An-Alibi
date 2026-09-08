from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Echoes of the Alibi API"
    app_env: str = "development"
    debug: bool = True
    api_prefix: str = "/api"
    database_url: str = "sqlite:///./echoes.db"
    jwt_secret_key: str = "replace-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 180
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    ollama_enabled: bool = True
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    ollama_timeout_seconds: int = 20
    ai_prompt_version: str = "v1"
    max_chat_message_length: int = 500
    interview_rate_limit: int = 40

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()
