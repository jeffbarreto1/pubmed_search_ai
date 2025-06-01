from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PUBMED_API_KEY = os.getenv("PUBMED_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

class Settings(BaseSettings):
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True

    # Google Gemini
    GEMINI_API_KEY: str

    # Tavily
    TAVILY_API_KEY: str

    # PubMed
    pubmed_email: Optional[str] = None
    PUBMED_API_KEY: Optional[str] = None

    # Session Management
    session_timeout_minutes: int = 30
    max_sessions: int = 1000

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"

def get_settings() -> Settings:
    return Settings()
