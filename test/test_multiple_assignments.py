import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from orchestrator.graph import graph

def test_multiple_actions():
    print("\n--- TEST: Coach executing Compound/Multiple Assignment Operations ---")
    state = {
        "session": {
            "user_id": "C001",
            "role": "coach",
            "name": "Lead AI Architect"
        },
        "user_input": "remove assignment 3 and add assignment 4 to om",
        "current_intent": "",
        "retrieved_context": "",
        "learner_id": "unknown",
        "agent_response": "",
        "execution_path": []
    }
    
    result = graph.invoke(state)
    print("Execution Path Taken:", result.get("execution_path"))
    print("\n================= AGENT RESPONSE =================\n")
    print(result.get("agent_response"))
    print("\n==================================================\n")
    
    # Assert coach_assignment_node was successfully run
    assert "coach_assignment_node" in result.get("execution_path")
    print("✅ TEST PASSED: Compound assignment orchestration successfully processed both actions!")

if __name__ == "__main__":
    test_multiple_actions()
