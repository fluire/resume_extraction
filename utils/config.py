from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional
import configparser
import os

class Settings(BaseSettings):
    s3_url: str = Field(..., env="S3_URL")
    s3_access_key: str = Field(..., env="S3_ACCESS_KEY")
    s3_secret_key: str = Field(..., env="S3_SECRET_KEY")
    mongo_uri: str = Field(..., env="MONGO_URI")
    mongo_username: str = Field(..., env="MONGO_USERNAME")
    mongo_password: str = Field(..., env="MONGO_PASSWORD")
    qdrant_uri: str = Field(..., env="QDRANT_URI")
    postgres_uri: str = Field(..., env="POSTGRES_URI")
    postgres_username: str = Field(..., env="POSTGRES_USERNAME")
    postgres_password: str = Field(..., env="POSTGRES_PASSWORD")
    llm_url_ollama: Optional[str] = Field(..., env="OLLAMA_URI")

    class Config:
        env_file = ".env"

def load_ini_config(ini_path: Optional[str] = None):
    ini_path = ini_path or os.path.join(os.path.dirname(__file__), '../config.ini')
    config = configparser.ConfigParser()
    config.read(ini_path)
    return {
        "s3_url": config.get("s3", "url"),
        "s3_access_key": config.get("s3", "access_key"),
        "s3_secret_key": config.get("s3", "secret_key"),
        "mongo_uri": config.get("mongodb", "uri"),
        "mongo_username": config.get("mongodb", "username"),
        "mongo_password": config.get("mongodb", "password"),
        "qdrant_uri": config.get("qdrant", "uri"),
        "postgres_uri": config.get("postgres", "uri"),
        "postgres_username": config.get("postgres", "username"),
        "postgres_password": config.get("postgres", "password"),
        "llm_url_ollama":config.get("ollama", "llm_url_ollama")
    }

# Load from .env or environment variables first, fallback to config.ini
try:
    settings = Settings()
except Exception:
    ini_vars = load_ini_config()
    settings = Settings(**ini_vars)