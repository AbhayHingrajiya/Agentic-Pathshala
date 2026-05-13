import logging

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

class DocumentChunker:
    def __init__(self, chunk_size=500, chunk_overlap=50):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = chunk_size,
            chunk_overlap = chunk_overlap,
            separators = ["\n\n", "\n", ".", " ", ""]
        )

    def chunk_documents(self, documents: list[Document]) -> list[Document]:
        chunk_documents = self.text_splitter.split_documents(documents)

        for index, chunk in enumerate(chunk_documents):
            chunk.metadata["chunk_id"] = index

        logger.info(
            "Chunked %s documents into %s chunks",
            len(documents),
            len(chunk_documents),
        )

        return chunk_documents
        