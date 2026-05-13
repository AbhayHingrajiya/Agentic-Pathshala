from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    GROQ_API_KEY: str
    CHROMA_PATH: str
    STORE_PATH: str
    MODEL_NAME: str
    MCP_SERVER_URL: str
    TEMPERATURE: float = 0.2
    
    class Config:
        env_file = ".env"    
        
settings = Settings()