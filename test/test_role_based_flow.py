import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from orchestrator.graph import graph

def test_learner_blocked():
    print("\n--- TEST 1: Learner attempting Coach Operation ---")
    state = {
        "session": {
            "user_id": "L001",
            "role": "learner",
            "name": "Bhavesh Gediya"
        },
        "user_input": "Assign Assignment 1 to all learners",
        "current_intent": "",
        "retrieved_context": "",
        "learner_id": "L001",
        "agent_response": "",
        "execution_path": []
    }
    
    result = graph.invoke(state)
    print("Execution Path Taken:", result.get("execution_path"))
    response = result.get("agent_response", "")
    if sys.stdout and hasattr(sys.stdout, 'encoding') and sys.stdout.encoding:
        try:
            response = response.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
        except Exception:
            pass
    print("Agent Response:\n", response)
    assert "general_agent_node" in result.get("execution_path")
    assert "coach_assignment_node" not in result.get("execution_path")
    print("[SUCCESS] TEST 1 PASSED: Learner was correctly blocked by RBAC Gateway!")

def test_coach_success():
    print("\n--- TEST 2: Coach executing Assignment Operation ---")
    state = {
        "session": {
            "user_id": "C001",
            "role": "coach",
            "name": "Lead AI Architect"
        },
        "user_input": "Assign Assignment 1 to beginners",
        "current_intent": "",
        "retrieved_context": "",
        "learner_id": "unknown",
        "agent_response": "",
        "execution_path": []
    }
    
    result = graph.invoke(state)
    print("Execution Path Taken:", result.get("execution_path"))
    response = result.get("agent_response", "")
    if sys.stdout and hasattr(sys.stdout, 'encoding') and sys.stdout.encoding:
        try:
            response = response.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
        except Exception:
            pass
    print("Agent Response:\n", response)
    assert "coach_assignment_node" in result.get("execution_path")
    print("[SUCCESS] TEST 2 PASSED: Coach successfully triggered assignment orchestration!")

if __name__ == "__main__":
    try:
        test_learner_blocked()
        # Note: test_coach_success requires the MCP server running. 
        # If the MCP server is off, it will catch the ConnectionError safely.
        print("\nChecking Coach flow (Note: Requires FastMCP server running)...")
        test_coach_success()
    except Exception as e:
        print(f"\nExecution encountered an issue: {str(e)}")
