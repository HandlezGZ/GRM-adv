from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "LexEval - Continuous AI Evaluation & Quality Monitoring"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./lexeval.db"
    FASTAPI_PORT: int = 8001
    STREAMLIT_PORT: int = 8502
    LOG_LEVEL: str = "INFO"
    BACKEND_URL: str = "http://127.0.0.1:8001"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
