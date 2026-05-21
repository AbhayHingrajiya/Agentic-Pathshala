from utils.prompt_loader import load_prompt
from utils.llm import llm
from mcp_server.mcp_client import call_mcp_tool

def progress_agent(state: dict) -> dict:
    learner_id = state.get("learner_id", "unknown")
    query = state.get("user_input", "")
    try:
        assignments_result = call_mcp_tool("get_assignments_for_learner", {"learner_id": learner_id})
        progress_result = call_mcp_tool("get_progress_for_learner", {"learner_id": learner_id})
        notes_result = call_mcp_tool("get_notes_for_learner", {"learner_id": learner_id})
        
        assignment_data = assignments_result.get("assignments", [])
        progress_data = progress_result.get("progress", [])
        notes_data = notes_result.get("notes", [])
    except Exception as e:
        assignment_data, progress_data, notes_data = [], [], []
        state.setdefault("execution_path", []).append(f"mcp_error: {str(e)}")
    prompt = load_prompt("progress_agent")
    chain = prompt | llm
    response = chain.invoke({
        "learner_id": learner_id,
        "assignment_data": str(assignment_data),
        "progress_data": str(progress_data),
        "notes_data": str(notes_data),
        "query": query
    })
    state["agent_response"] = response.content.strip()
    state.setdefault("execution_path", []).append("progress_agent")
    return state