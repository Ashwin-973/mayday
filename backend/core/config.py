"""
Configuration management using Pydantic Settings.
Loads environment variables from .env file and validates required fields.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    openweather_api_key: str
    twelvedata_api_key: str
    
    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    
    # API Configuration
    openweather_geo_url: str = "http://api.openweathermap.org/geo/1.0/direct"
    openweather_weather_url: str = "https://api.openweathermap.org/data/2.5/weather"
    twelvedata_quote_url: str = "https://api.twelvedata.com/quote"
    
    # Request timeouts (seconds)
    api_timeout: int = 10
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Using lru_cache ensures settings are loaded only once.
    """
    return Settings()
