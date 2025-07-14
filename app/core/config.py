# config/settings.py

from pydantic_settings import BaseSettings
from pydantic import Field, ValidationError
from typing import Literal

class Settings(BaseSettings):
    mongodb_uri: str = Field(..., env="MONGODB_URI")
    jwt_secret: str = Field(..., env="JWT_SECRET")
    algorithm: Literal["HS256"] = "HS256"
    token_expire_minutes: int = 1440  

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

try:
    settings = Settings()
except ValidationError as e:
    raise RuntimeError(f"Environment configuration error: {e}")
