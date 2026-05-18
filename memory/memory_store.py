import uuid
import logging
import hashlib
from datetime import datetime
from langchain_chroma import Chroma
from langchain_core.documents import Document
from rag import get_embeddings
from config.settings import settings

logger = logging.getLogger(__name__)

_memory_store = None

def get_memory_store() -> Chroma:
    """
    Returns a singleton Chroma collection dedicated to learner memories.
    Uses the SAME embedding model as RAG but a DIFFERENT collection name.
    """
    global _memory_store
    if _memory_store is None:
        logger.info("Loading memory store...")
        _memory_store = Chroma(
            collection_name=settings.MEMORY_COLLECTION_NAME,
            embedding_function=get_embeddings(),
            persist_directory=str(settings.CHROMA_PATH),
        )
        logger.info("Memory store loaded.")
    return _memory_store

def _content_hash(self, text: str):
    """
    Creates a short unique ID for a memory text.
    Why MD5? Not for security — just for fast, deterministic deduplication.
    Two identical memory strings will always produce the same hash.
    """
    return hashlib.md5(text.strip().lower().encode()).hexdigest()

def save_memory_if_new(self, learner_id: str, memory_text: str) -> bool:
    """
    Saves a memory ONLY if semantically identical content doesn't already exist.
    Strategy: Use the content hash as the ChromaDB document ID.
    ChromaDB IDs must be unique — if we try to add a duplicate ID, it will
    raise an error. We catch that error and return False (already exists).
    Why not query first?
    Querying ChromaDB for each memory before saving costs a vector search.
    Using IDs is O(1) and deterministic.
    Returns True if saved, False if already existed.
    """
    store = get_memory_store()
    doc_id = f"{learner_id}_{self._content_hash(memory_text)}"
    doc = Document(
        page_content=memory_text,
        metadata={
            "learner_id": learner_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
    try:
        store.add_documents(documents=[doc], ids=[doc_id])
        logger.info("Memory saved [%s]: %s", learner_id, memory_text)
        return True
    except Exception:
        # ChromaDB raises if ID already exists → memory is a duplicate
        logger.debug("Memory already exists, skipping [%s]: %s", learner_id, memory_text)
        return False    

class MemoryStore:

    def save_memory(self, learner_id: str, memory_text: str) -> None:
        """
        Saves a single memory fact for a learner.
        Why uuid? Each memory needs a unique ID so ChromaDB can store
        multiple memories without overwriting each other.
        Why timestamp? So we could later sort memories by recency if needed.
        """
        store = get_memory_store()
        doc = Document(
            page_content=memory_text,
            metadata={
                "learner_id": learner_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        store.add_documents(documents=[doc], ids=[str(uuid.uuid4())])
        logger.info("Memory saved for learner %s: %s", learner_id, memory_text)


    def retrieve_memories(self, learner_id: str, query: str, k: int = 5) -> list[str]:
        """
        Retrieves the most semantically relevant past memories for a learner.
        Why filter by learner_id? So L001's memories are never shown to L002.
        Why semantic search (not just load all)? Returns only RELEVANT memories
        for the current conversation — not everything ever stored.
        """
        store = get_memory_store()
        results = store.similarity_search(
            query=query,
            k=k,
            filter={"learner_id": learner_id}  
        )
        return [doc.page_content for doc in results]

    def get_all_memories(self, learner_id: str) -> list[str]:
        """
        Returns ALL memories for a learner (for debugging/admin purposes).
        Not used in normal graph flow.
        """
        store = get_memory_store()
        results = store.similarity_search(
            query="learner history",
            k=100,
            filter={"learner_id": learner_id}
        )
        return [doc.page_content for doc in results]

