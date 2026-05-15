from .state import CoachState
from utils import load_prompt
from agents import coordinator_agent, notes_agent, assessment_agent

# -----------------------------
# NODE FUNCTIONS
# -----------------------------

def coordinator_node(state: CoachState) -> dict:
    try:
        path = state.get("execution_path", [])
        path.append("coordinator_node")
        state["execution_path"] = path

        updated_state = coordinator_agent(state)
        
        return {
            "current_intent": updated_state["current_intent"],
            "execution_path": updated_state["execution_path"]
        }
    except Exception as e:
        return {"agent_response": f"Error: {str(e)}"}

def notes_agent_node(state: CoachState) -> dict:
    try:
        path = state.get("execution_path", [])
        path.append("notes_agent_node")
        state["execution_path"] = path

        updated_state = notes_agent(state)
        
        return {
            "agent_response": updated_state["agent_response"],
            "retrieved_context": updated_state["retrieved_context"],
            "execution_path": updated_state["execution_path"]
        }
    except Exception as e:
        return {"agent_response": f"Error in Notes Agent: {str(e)}"}

def assessment_agent_node(state: CoachState) -> dict:
    try:
        path = state.get("execution_path", [])
        path.append("assessment_agent_node")
        state["execution_path"] = path

        updated_state = assessment_agent(state)
        
        return {
            "agent_response": updated_state["agent_response"],
            "retrieved_context": updated_state["retrieved_context"],
            "execution_path": updated_state["execution_path"]
        }
    except Exception as e:
        return {"agent_response": f"Error in Assessment Agent: {str(e)}"}

def response_node(state: CoachState) -> dict:
    try:
        path = state.get("execution_path", [])
        path.append("response_node")
        
        return {
            "execution_path": path
        }
    except Exception as e:
        return {"agent_response": f"Error in Response Node: {str(e)}"}

def fallback_node(state: CoachState) -> dict:
    try:
        path = state.get("execution_path", [])
        path.append("fallback_node")
        
        return {
            "agent_response": "I'm not sure how to help with that. Could you try asking about a specific learning concept?",
            "execution_path": path
        }
    except Exception as e:
        return {"agent_response": str(e)}
