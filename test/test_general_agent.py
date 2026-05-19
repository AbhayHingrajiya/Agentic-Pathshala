import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from orchestrator.graph import graph

def test_general_agent_flow():
    print("\n==================================================")
    print("🚀 STARTING TEST: GENERAL AGENT ROUTING & ANSWERS")
    print("==================================================\n")

    # 1. Test case: General knowledge question
    print("--- STEP 1: Querying Capital of Gujarat ---")
    state_gk = {
        "user_input": "what is the capital of Gujarat?",
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
    
    res = graph.invoke(state_gk)
    print("Execution Path:", res.get("execution_path"))
    print("AI Response:", res.get("agent_response"))
    assert "general_agent" in res.get("execution_path")
    assert "gandhinagar" in res.get("agent_response").lower()
    print("✅ STEP 1 PASSED: General knowledge query successfully answered!")

    # 2. Test case: Casual greeting
    print("\n--- STEP 2: Casual Greeting Query ---")
    state_greeting = {
        "user_input": "How are you?",
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
    
    res = graph.invoke(state_greeting)
    print("Execution Path:", res.get("execution_path"))
    print("AI Response:", res.get("agent_response"))
    assert "general_agent" in res.get("execution_path")
    assert len(res.get("agent_response")) > 0
    print("✅ STEP 2 PASSED: Casual greeting query successfully answered!")

    print("\n==================================================")
    print("🎉 ALL TESTS PASSED: GENERAL AGENT INTEGRATED PERFECTLY!")
    print("==================================================\n")

if __name__ == "__main__":
    test_general_agent_flow()
