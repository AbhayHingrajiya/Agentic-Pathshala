from langchain_core.documents import Document
from rag import DocumentChunker
import logging

logging.basicConfig(level=logging.INFO)

documents = [
    Document(
        page_content="""
        Retrieval-Augmented Generation (RAG) combines
        vector search with language models.
        It improves factual accuracy.
        """,
        metadata={"source": "rag_intro.md"},
    )
]

chunker = DocumentChunker()

chunks = chunker.chunk_documents(documents)

for chunk in chunks:
    print("\n--- CHUNK ---")
    print(chunk.page_content)
    print(chunk.metadata)