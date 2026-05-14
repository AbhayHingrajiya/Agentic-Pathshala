# pyrefly: ignore [missing-import]
from langchain_groq import ChatGroq
from config.settings import settings

llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model=settings.MODEL_NAME,
    temperature=settings.TEMPERATURE
)