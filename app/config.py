import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "AI Support Ticket Analytics"
    ENVIRONMENT: str = "development"

    DATA_PATH: str = "support_tickets.csv"
    DATABASE_PATH: str = "support_tickets.db"

    LLM_PROVIDER: str = "ollama"
    LLM_MODEL: str = "llama3.2"
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    ANOMALY_RESOLUTION_THRESHOLD_HOURS: float = 24.0
    ANOMALY_RESPONSE_THRESHOLD_HOURS: float = 4.0
    LOW_RATING_THRESHOLD: float = 2.0
    STATISTICAL_Z_THRESHOLD: float = 2.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

settings = Settings()
