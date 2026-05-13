import logging

from config import settings

from rag import DocumentChunker, get_vectorstore, reset_collection, load_documents

logger = logging.getLogger(__name__)

def ingest_documents() -> None:
    """Ingest documents into the vector store."""
    
    logger.info("Starting document ingestion...")

    documents = load_documents()
    if not documents:
        logger.warning("No documents found to ingest")
        return
    
    chunker = DocumentChunker()
    chunks = chunker.chunk_documents(documents)

    logger.info("Ingested %s chunks", len(chunks))

    reset_collection()

    vectorstore = get_vectorstore()
    vectorstore.add_documents(chunks)
    logger.info("Document ingestion completed.")