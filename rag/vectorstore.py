import logging

from langchain_chroma import Chroma


from rag import get_embeddings
from config import settings

logger = logging.getLogger(__name__)

_vectorstore = None

def get_vectorstore() -> Chroma:
    """
    Returns a singleton instance of the vector store
    """
    global _vectorstore

    if _vectorstore is None:
        logger.info("Loading vectorstore")
        _vectorstore = Chroma(
            collection_name = settings.COLLECTION_NAME,
            embedding_function = get_embeddings(),
            persist_directory = str(settings.CHROMA_PATH),
        )
        logger.info("Vector store loaded successfully")
    
    return _vectorstore

def reset_collection():
    global _vectorstore
    logger.warning("Resetting ChromaDB collection...")

    vectorstore = get_vectorstore()

    vectorstore.delete_collection()

    _vectorstore = None

    logger.info("Collection reset successfully")