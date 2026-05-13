from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    #API Keys
    GROQ_API_KEY: str

    # Paths
    CHROMA_PATH: Path = BASE_DIR / "data" / "chroma_db"
    DOCUMENTS_PATH: Path = BASE_DIR / "data" / "documents"
    STORE_PATH: Path = BASE_DIR / "data" / "storage"

    # Models
    MODEL_NAME: str = "llama-3.3-70b-versatile"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Vector DB
    COLLECTION_NAME: str = "learning_coach_kb"

    # MCP
    MCP_SERVER_URL: str = "http://localhost:8000/mcp"

    #Settings Config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

settings = Settings() #this creates a singelton instance of settings
