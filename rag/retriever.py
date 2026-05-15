import logging

from langchain_core.documents import Document

from rag import get_vectorstore

from config.settings import settings

logger = logging.getLogger(__name__)



def retrieve_documents(query: str, k: int = 5) -> list[Document]:
    """Retrieve relevant documents from the vector store"""

    logger.info("Retrieving documents for query: %s", query)

    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search_with_score(query, k=k)

    filtered_results = [
        (document, score)
        for document, score in results
        if score <= settings.MAX_SIMILARITY_SCORE
    ]

    logger.info("Retrieved %s documents", len(filtered_results))

    return filtered_results