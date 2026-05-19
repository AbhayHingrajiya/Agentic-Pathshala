import logging
from pathlib import Path

from utils import load_prompt, llm
from rag import retrieve_documents, get_vectorstore
from config import settings
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

def notes_agent(state):
    query = state["user_input"]
    learner_id = state.get("learner_id", "unknown")
    
    # 1. Robust plain-text classification and extraction using a strict few-shot classifier prompt loaded from YAML
    parser_prompt = load_prompt("notes_classifier")
    
    action = "query"
    note_content = ""
    
    try:
        chain = parser_prompt | llm
        response = chain.invoke({"query": query})
        response_text = response.content.strip()
        logger.info("Notes Agent Parser raw response: %s", response_text)
        
        for line in response_text.split("\n"):
            if line.upper().startswith("ACTION:"):
                action = line.split(":", 1)[1].strip().lower()
            elif line.upper().startswith("CONTENT:"):
                note_content = line.split(":", 1)[1].strip()
                
        # Clean up any surrounding quotes added by the LLM
        if note_content.startswith("'") and note_content.endswith("'"):
            note_content = note_content[1:-1]
        elif note_content.startswith('"') and note_content.endswith('"'):
            note_content = note_content[1:-1]
            
    except Exception as e:
        logger.error("Failed to parse notes agent intent, falling back to query.", exc_info=True)
        action = "query"
        note_content = ""

    if action == "save" and note_content:
        note_text = note_content.strip()
        logger.info("Saving new personal note for learner %s: %s", learner_id, note_text)

        # A. Append to the learner's text file on disk
        file_path = settings.DOCUMENTS_PATH / f"notes_{learner_id}.txt"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(note_text + "\n")

        # B. Dynamically embed the note in ChromaDB for immediate searchability
        new_doc = Document(
            page_content=note_text,
            metadata={
                "source": f"notes_{learner_id}.txt",
                "document_type": "documents",
                "learner_id": learner_id
            }
        )
        try:
            vectorstore = get_vectorstore()
            vectorstore.add_documents([new_doc])
            logger.info("Dynamically added note to vector store for learner %s", learner_id)
        except Exception as e:
            logger.warning("Dynamic embed failed (perhaps due to external database recreation). Auto-healing reference refresh...", exc_info=True)
            try:
                import rag.vectorstore
                rag.vectorstore._vectorstore = None
                vectorstore = get_vectorstore()
                vectorstore.add_documents([new_doc])
                logger.info("Dynamically added note to vector store after self-healing refresh.")
            except Exception as retry_err:
                logger.error("Failed to dynamically embed new note in ChromaDB even after refresh", exc_info=retry_err)

        state["agent_response"] = f"📝 I have successfully noted that down for you: \"{note_text}\""
        state["retrieved_context"] = f"[Saved Note] {note_text}"
        state["execution_path"].append("notes_agent")
        return state

    else:
        # Action is query - perform RAG retrieval with learner isolation
        results = retrieve_documents(query, learner_id=learner_id, k=5)
        
        context = "\n\n".join([doc.page_content for doc, score in results])
        
        prompt = load_prompt("notes_agent")
        chain = prompt | llm
        
        response = chain.invoke({
            "context": context,
            "query": query,
            "memory_context": state.get("memory_context", "No past memories.")
        })
        
        state["agent_response"] = response.content
        state["retrieved_context"] = context
        state["execution_path"].append("notes_agent")
        
        return state
