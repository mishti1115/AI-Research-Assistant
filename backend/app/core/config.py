"""
Application configuration loaded from environment variables.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "AI Research Paper Assistant"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # --- LLM Provider ---
    # Defaults to Ollama: fully local, free, no API key or internet required
    # (beyond the one-time `ollama pull` of the model). "openai" and "gemini"
    # remain supported if you ever want to switch to a hosted model.
    LLM_PROVIDER: str = "ollama"  # "ollama" | "openai" | "gemini"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_CHAT_MODEL: str = "llama3.2"  # run `ollama pull llama3.2` first

    OPENAI_API_KEY: str = ""
    OPENAI_CHAT_MODEL: str = "gpt-4.1"
    GEMINI_API_KEY: str = ""
    GEMINI_CHAT_MODEL: str = "gemini-2.5-pro"

    # --- Embeddings ---
    # Free, local, CPU-friendly sentence-transformers model — no API key,
    # no cost, downloaded once from HuggingFace Hub and cached locally.
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # --- RAG ---
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 150
    TOP_K: int = 6
    VECTOR_STORE_DIR: str = "app/data/vector_store"
    UPLOAD_DIR: str = "app/data/uploads"

    # --- Server ---
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    MAX_UPLOAD_MB: int = 50

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton so we don't re-read .env on every call."""
    return Settings()
