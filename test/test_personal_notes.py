import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import settings
from rag.ingestion import ingest_documents
from orchestrator.graph import graph

def test_personal_notes_flow():
    print("\n==================================================")
    print("🚀 STARTING TEST: PERSONAL NOTES FLOW & ISOLATION")
    print("==================================================\n")

    # 1. Clean up any existing test note files
    note_file_l001 = settings.DOCUMENTS_PATH / "notes_L001.txt"
    note_file_l002 = settings.DOCUMENTS_PATH / "notes_L002.txt"

    if note_file_l001.exists():
        os.remove(note_file_l001)
    if note_file_l002.exists():
        os.remove(note_file_l002)

    print("🧹 Cleaned up old test note files.")

    # 2. Reset Chroma and trigger baseline ingestion
    print("\n📥 Performing baseline database ingestion...")
    ingest_documents()
    print("✅ Ingestion baseline established.")

    # 3. Learner L001 (Om) saves a note
    print("\n--- STEP 1: Learner L001 (Om) records a note ---")
    state_save_l001 = {
        "user_input": "take a note 'i like python more than java'",
        "learner_id": "L001",
        "session": {
            "user_id": "L001",
            "role": "learner",
            "name": "Om Chauhan"
        },
        "current_intent": "",
        "retrieved_context": "",
        "agent_response": "",
        "execution_path": []
    }
    res = graph.invoke(state_save_l001)
    print("Execution Path:", res.get("execution_path"))
    print("AI Response:", res.get("agent_response"))
    assert "notes_agent" in res.get("execution_path")
    assert "python" in res.get("agent_response").lower()
    print("✅ STEP 1 PASSED: L001 successfully recorded note!")

    # 4. Learner L002 (Bhavesh) saves a different note
    print("\n--- STEP 2: Learner L002 (Bhavesh) records a note ---")
    state_save_l002 = {
        "user_input": "take a note 'my favorite language is javascript'",
        "learner_id": "L002",
        "session": {
            "user_id": "L002",
            "role": "learner",
            "name": "Bhavesh Gediya"
        },
        "current_intent": "",
        "retrieved_context": "",
        "agent_response": "",
        "execution_path": []
    }
    res = graph.invoke(state_save_l002)
    print("Execution Path:", res.get("execution_path"))
    print("AI Response:", res.get("agent_response"))
    assert "notes_agent" in res.get("execution_path")
    assert "javascript" in res.get("agent_response").lower()
    print("✅ STEP 2 PASSED: L002 successfully recorded note!")

    # 5. Verify Learner L001's query (Should only see L001 notes and NOT L002 notes)
    print("\n--- STEP 3: Learner L001 (Om) queries preferences (Privacy Check) ---")
    state_query_l001 = {
        "user_input": "what language do I prefer?",
        "learner_id": "L001",
        "session": {
            "user_id": "L001",
            "role": "learner",
            "name": "Om Chauhan"
        },
        "current_intent": "",
        "retrieved_context": "",
        "agent_response": "",
        "execution_path": []
    }
    res = graph.invoke(state_query_l001)
    print("Execution Path:", res.get("execution_path"))
    print("AI Response:", res.get("agent_response"))
    
    # Assert they get python answer
    assert "python" in res.get("agent_response").lower()
    # Assert they do NOT get L002's javascript note
    assert "javascript" not in res.get("agent_response").lower()
    print("✅ STEP 3 PASSED: L001 query was accurate and isolated!")

    # 6. Verify Learner L002's query (Should only see L002 notes and NOT L001 notes)
    print("\n--- STEP 4: Learner L002 (Bhavesh) queries preferences (Privacy Check) ---")
    state_query_l002 = {
        "user_input": "what is my favorite language?",
        "learner_id": "L002",
        "session": {
            "user_id": "L002",
            "role": "learner",
            "name": "Bhavesh Gediya"
        },
        "current_intent": "",
        "retrieved_context": "",
        "agent_response": "",
        "execution_path": []
    }
    res = graph.invoke(state_query_l002)
    print("Execution Path:", res.get("execution_path"))
    print("AI Response:", res.get("agent_response"))
    
    # Assert they get javascript answer
    assert "javascript" in res.get("agent_response").lower()
    # Assert they do NOT get L001's python/java notes
    assert "python" not in res.get("agent_response").lower()
    print("✅ STEP 4 PASSED: L002 query was accurate and isolated!")

    print("\n==================================================")
    print("🎉 ALL TESTS PASSED: E2E PERSONAL NOTES WORKS PERFECTLY!")
    print("==================================================\n")

if __name__ == "__main__":
    test_personal_notes_flow()
