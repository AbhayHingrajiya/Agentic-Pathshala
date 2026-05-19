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

    # Safely clear all documents inside the collection instead of physically destroying the collection.
    # This prevents orphaned UUID collection NotFoundErrors in running client processes.
    try:
        all_docs = vectorstore.get()
        if all_docs and "ids" in all_docs and all_docs["ids"]:
            vectorstore.delete(ids=all_docs["ids"])
            logger.info("Safely cleared %d documents from collection", len(all_docs["ids"]))
    except Exception as e:
        logger.warning("Direct clear failed, falling back to delete_collection: %s", e)
        vectorstore.delete_collection()

    _vectorstore = None

    logger.info("Collection reset successfully")