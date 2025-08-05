# config/settings.py

from pydantic_settings import BaseSettings
from pydantic import Field, ValidationError
from typing import Literal, ClassVar

class Settings(BaseSettings):
    mongodb_uri: str = Field(..., env="MONGODB_URI")
    jwt_secret: str = Field(..., env="JWT_SECRET")
    algorithm: Literal["HS256"] = "HS256"
    token_expire_minutes: int = 1440
    log_level:str ="INFO"  
    OPENAI_API_KEY:str=Field(..., env="OPENAI_API_KEY")
    PINECONE_API_KEY:str=Field(..., env="PINECONE_API_KEY")
    PINECONE_ENV:str=Field(..., env="PINECONE_ENV")
    PINECONE_INDEX_NAME:str = "rag-1-langchain-index"
    
    EMBEDDING_MODEL: ClassVar[str] = "text-embedding-ada-002"
    CHUNK_OVERLAP: ClassVar[int] = 100
    CHUNK_SIZE: ClassVar[int] = 500

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

try:
    settings = Settings()
except ValidationError as e:
    raise RuntimeError(f"Environment configuration error: {e}")
