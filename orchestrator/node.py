from .state import CoachState
from utils import load_prompt
from agents import coordinator_agent, notes_agent, assessment_agent, evaluator_agent
from agents.assignment_agent import assignment_agent
from agents.recommendation_agent import recommendation_agent
from memory.memory_store import MemoryStore
from memory.memory_extractor import extract_memories

# -----------------------------
# NODE FUNCTIONS
# -----------------------------

memory_store = MemoryStore()

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

def evaluator_agent_node(state: CoachState) -> dict:
    try:
        path = state.get("execution_path", [])
        path.append("evaluator_agent_node")
        state["execution_path"] = path

        updated_state = evaluator_agent(state)
        
        return {
            "agent_response": updated_state["agent_response"],
            "retrieved_context": updated_state["retrieved_context"],
            "execution_path": updated_state["execution_path"]
        }
    except Exception as e:
        return {"agent_response": f"Error in Evaluator Agent: {str(e)}"}

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

def assignment_node(state: CoachState) -> dict:
    try:
        path = state.get("execution_path", [])
        path.append("assignment_node")
        state["execution_path"] = path
        updated_state = assignment_agent(state)
        return {
            "agent_response": updated_state.get("agent_response", "No response generated."),
            "execution_path": updated_state.get("execution_path", path)
        }
    except Exception as e:
        return {
            "agent_response": f"Error in Assignment Agent: {str(e)}",
            "execution_path": state.get("execution_path", []) + ["assignment_node_error"]
        }

def recommendation_node(state: CoachState) -> dict:
    try:
        path = state.get("execution_path", [])
        path.append("recommendation_node")
        state["execution_path"] = path
        updated_state = recommendation_agent(state)
        return {
            "agent_response": updated_state.get("agent_response", "No recommendation generated."),
            "execution_path": updated_state.get("execution_path", path)
        }
    except Exception as e:
        return {
            "agent_response": f"Error in Recommendation Agent: {str(e)}",
            "execution_path": state.get("execution_path", []) + ["recommendation_node_error"]
        }

def memory_reader_node(state: CoachState) -> dict:
    """
    Runs FIRST in the graph.
    What it does:
    1. Looks up past memories for this learner from ChromaDB
    2. Formats them into a readable paragraph
    3. Stores in state["memory_context"] so ALL agents can access them
    Why run at START?
    The coordinator and agents need past context BEFORE they respond.
    If we loaded memories later, they wouldn't inform this conversation's response.
    """
    try:
        path = state.get("execution_path", [])
        path.append("memory_reader_node")
        learner_id = state.get("learner_id", "unknown")
        user_input = state.get("user_input", "")
        # Retrieve memories semantically relevant to this query
        memories = memory_store.retrieve_memories(
            learner_id=learner_id,
            query=user_input,
            k=5
        )
        if memories:
            memory_context = "What I remember about this learner:\n" + "\n".join(
                f"- {m}" for m in memories
            )
        else:
            memory_context = "No previous memories found for this learner."
        return {
            "memory_context": memory_context,
            "execution_path": path
        }
    except Exception as e:
        return {
            "memory_context": "Memory unavailable.",
            "execution_path": state.get("execution_path", []) + ["memory_reader_error"]
        }

def memory_writer_node(state: CoachState) -> dict:
    """
    Runs LAST in the graph (after response_node).
    What it does:
    1. Sends the conversation exchange to the memory extractor LLM
    2. Gets back a list of important facts
    3. Saves each fact to ChromaDB with the learner's ID as metadata
    Why run at END?
    We need the final agent_response before we can extract memories from it.
    Running at the end ensures we capture what was actually said.
    Why NOT block the response?
    This node returns {"execution_path": ...} only — it doesn't change
    agent_response, so the user already received their answer before this runs.
    """
    try:
        path = state.get("execution_path", [])
        path.append("memory_writer_node")
        learner_id = state.get("learner_id", "unknown")
        user_input = state.get("user_input", "")
        agent_response = state.get("agent_response", "")
        # Extract facts worth remembering
        memories = extract_memories(
            learner_id=learner_id,
            user_input=user_input,
            agent_response=agent_response
        )
        # Save each memory fact to ChromaDB
        for memory_text in memories:
            memory_store.save_memory_if_new(learner_id, memory_text)
        return {"execution_path": path}
    except Exception as e:
        # Never crash here — memory saving is non-critical
        return {
            "execution_path": state.get("execution_path", []) + ["memory_writer_error"]
        }