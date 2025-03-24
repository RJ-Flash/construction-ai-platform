import secrets
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Construction AI Platform API"
    PROJECT_DESCRIPTION: str = "API for the Construction AI Platform"
    PROJECT_VERSION: str = "0.1.0"
    
    # SECURITY
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    ALGORITHM: str = "HS256"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://construction-ai-platform.example.com",
    ]
    
    # Validate CORS origins
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # DATABASE
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost/construction_ai"
    )
    
    # UPLOAD DIRECTORIES
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    DOCUMENT_UPLOAD_DIR: str = os.path.join(UPLOAD_DIR, "documents")
    
    # OUTPUT DIRECTORIES
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "outputs")
    PDF_OUTPUT_DIR: str = os.path.join(OUTPUT_DIR, "pdfs")
    
    # OPENAI SETTINGS
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # STRIPE SETTINGS (for future payment integration)
    STRIPE_API_KEY: Optional[str] = os.getenv("STRIPE_API_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.DOCUMENT_UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.PDF_OUTPUT_DIR, exist_ok=True)
