import logging
import re

from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_core.documents import Document

from config import settings

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = [".txt",".pdf", ".md", ".docx"]

def load_single_document(file_path: Path) -> list[Document]:

    try:
        if file_path.suffix == ".pdf":
            loader = PyPDFLoader(str(file_path))
        elif file_path.suffix in [".txt", ".md"]:
            loader = TextLoader(str(file_path))
        elif file_path.suffix == ".docx":
            loader = Docx2txtLoader(str(file_path))
        else:
            logger.warning("Skipping unsupported file: %s", file_path.name)
            return []

        documents = loader.load()

        document_type = file_path.parent.name

        # Determine learner_id for isolation:
        # If it's a personal note file (e.g., notes_L001.txt), extract L001.
        # Otherwise, tag as "system".
        if file_path.name.startswith("notes_"):
            match = re.match(r"^notes_([A-Za-z0-9_]+)\.", file_path.name)
            learner_id = match.group(1) if match else "unknown"
        else:
            learner_id = "system"

        for document in documents:
            document.metadata["source"] = file_path.name
            document.metadata["document_type"] = document_type
            document.metadata["learner_id"] = learner_id

        return documents

    except Exception as e:
        logger.error("Failed to load document: %s", file_path.name, exc_info=True)
    return []

def load_documents() -> list[Document]:
    """Load all documents from the documents directory"""

    documents = []

    document_path = settings.DOCUMENTS_PATH

    if not document_path.exists():
        logger.warning("Documents path does not exist: %s", document_path)
        return documents

    for file_path in document_path.rglob("*"):

        if not file_path.is_file():
            continue

        if file_path.suffix not in SUPPORTED_EXTENSIONS:
            logger.info("Skipping unsupported file: %s", file_path)
            continue

        logger.info("Loading document: %s", file_path.name)
        
        loaded_docs = load_single_document(file_path)

        documents.extend(loaded_docs)

    logger.info("Loaded %s total documents", len(documents))

    return documents