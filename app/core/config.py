# app/core/config.py
from functools import lru_cache
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Futurisys ML Service POC"

    API_KEY: str = Field(default="change")

    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)
    POSTGRES_DB: str = Field(default="mldb")
    POSTGRES_USER: str = Field(default="smail")
    POSTGRES_PASSWORD: str = Field(default="smail")
    
    model_path: str = Field(default="./models/model.pkl")

    
    database_url_env: str | None = Field(default=None, alias="DATABASE_URL")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True,                
        protected_namespaces=('settings_',),  
    )

    @property
    def database_url(self) -> str:
        """Construit l'URL SQLAlchemy avec psycopg (v3).
        if self.database_url_env:
            return self.database_url_env  
        user = self.POSTGRES_USER
        pwd  = quote_plus(self.POSTGRES_PASSWORD or "")
        host = self.POSTGRES_HOST
        port = self.POSTGRES_PORT
        db   = self.POSTGRES_DB
        # driver psycopg v3
        return f"postgresql+psycopg://{user}:{pwd}@{host}:{port}/{db}"
        """
        if self.database_url_env:  # override complet
            return self.database_url_env        
        
        return "sqlite:////data/app.db" 

    @property
    def DATABASE_URL(self) -> str:        
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
