"""Centralized configuration management using Pydantic Settings."""
from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application settings with environment variable overrides."""
    
    # App General
    APP_NAME: str = "Equestrian Compliance & Specification Auditor"
    APP_ENV: Literal["development", "testing", "production"] = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # Gemini API
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL_NAME: str = "gemini-2.0-flash"
    GEMINI_EMBEDDING_MODEL: str = "text-embedding-004"
    USE_MOCK_LLM: bool = False
    
    # Storage Directories
    QDRANT_STORAGE_PATH: str = str(BASE_DIR / "storage" / "qdrant")
    QDRANT_COLLECTION_NAME: str = "equestrian_regulations"
    UPLOAD_DIR: str = str(BASE_DIR / "storage" / "uploads")
    CACHE_DIR: str = str(BASE_DIR / "storage" / "cache")
    FIGURE_EXPORT_DIR: str = str(BASE_DIR / "storage" / "figures")
    
    # Rules & Knowledge Base
    FEI_REGULATIONS_DIR: str = str(BASE_DIR / "app" / "data" / "regulations" / "fei")
    BRAND_SOPS_DIR: str = str(BASE_DIR / "app" / "data" / "regulations" / "brand")
    RULES_CATALOG_PATH: str = str(BASE_DIR / "app" / "data" / "rules_catalog.json")

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def ensure_directories(self) -> None:
        """Create necessary storage directories if they do not exist."""
        for path_str in [
            self.QDRANT_STORAGE_PATH,
            self.UPLOAD_DIR,
            self.CACHE_DIR,
            self.FIGURE_EXPORT_DIR,
            self.FEI_REGULATIONS_DIR,
            self.BRAND_SOPS_DIR,
        ]:
            Path(path_str).mkdir(parents=True, exist_ok=True)


settings = Settings()
