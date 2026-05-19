import logging

from langchain_core.documents import Document

from rag import get_vectorstore

from config.settings import settings

logger = logging.getLogger(__name__)



from typing import Optional

def retrieve_documents(query: str, learner_id: Optional[str] = None, k: int = 5) -> list[Document]:
    """Retrieve relevant documents from the vector store with optional learner isolation"""

    logger.info("Retrieving documents for query: %s (learner_id: %s)", query, learner_id)

    vectorstore = get_vectorstore()
    
    # Filter documents to only include "system" documents and the current learner's notes.
    # This prevents cross-learner data leakage.
    query_filter = None
    if learner_id:
        query_filter = {
            "learner_id": {
                "$in": ["system", learner_id]
            }
        }

    results = vectorstore.similarity_search_with_score(query, k=k, filter=query_filter)

    filtered_results = [
        (document, score)
        for document, score in results
        if score <= settings.MAX_SIMILARITY_SCORE
    ]

    logger.info("Retrieved %s documents", len(filtered_results))

    return filtered_results