from pydantic_settings import BaseSettings
from typing import Optional
from enum import Enum

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

class Settings(BaseSettings):
    # API Keys
    MEM0_API_KEY: str
    OPENROUTER_API_KEY: str
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Model Settings
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    ANTHROPIC_MODEL: Optional[str] = "claude-v1"
    
    # Agent Settings
    LOG_LEVEL: LogLevel = LogLevel.INFO
    MAX_RETRIES: int = 3
    MAX_REACT_STEPS: int = 6
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
