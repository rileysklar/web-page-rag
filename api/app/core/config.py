"""
Configuration settings for the API.
"""
from typing import List
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    """API settings."""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "RAG API"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",    # Next.js default
        "http://localhost:4321",    # Astro default
        "http://localhost:5173",    # Vite default
        "http://localhost:8000",    # API default
    ]
    
    # Security
    API_KEY_NAME: str = "X-API-Key"
    API_KEY: str = os.getenv("API_KEY", "development_key")
    
    # RAG Configuration
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DEFAULT_MODEL_NAME: str = "gpt-3.5-turbo"
    DEFAULT_TEMPERATURE: float = 0.0
    
    class Config:
        """Pydantic config."""
        case_sensitive = True

# Create settings instance
settings = Settings() 