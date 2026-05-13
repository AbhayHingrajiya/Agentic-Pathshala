import logging
from langchain_huggingface import HuggingFaceEmbeddings

from config import settings

logger = logging.getLogger(__name__)

_embeddings = None

def get_embeddings() -> HuggingFaceEmbeddings:
    """
    Returns a singleton instance of the embedding generator
    """
    global _embeddings

    if _embeddings is None:
        logger.info("Loading embeddings")
        _embeddings = HuggingFaceEmbeddings(
            model_name = settings.EMBEDDING_MODEL
        )
        logger.info("Embedding model loaded successfully")
    
    return _embeddings