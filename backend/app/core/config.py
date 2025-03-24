from typing import List, Optional, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Construction AI Platform"
    API_V1_STR: str = "/api/v1"
    
    # SECURITY
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode='before')
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # DATABASE
    MYSQL_SERVER: str = "localhost"
    MYSQL_USER: str = "username"
    MYSQL_PASSWORD: str = "password"
    MYSQL_DB: str = "construction_ai"
    MYSQL_PORT: str = "3306"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode='before')
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        return f"mysql+pymysql://{values.data.get('MYSQL_USER')}:{values.data.get('MYSQL_PASSWORD')}@{values.data.get('MYSQL_SERVER')}:{values.data.get('MYSQL_PORT')}/{values.data.get('MYSQL_DB')}"
    
    # FILE STORAGE
    UPLOAD_FOLDER: str = "/uploads"
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "dwg", "ifc", "rvt"]
    
    # AI MODELS
    MODEL_PATH: str = "./models"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
