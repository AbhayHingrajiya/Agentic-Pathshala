import requests
from utils.prompt_loader import load_prompt
from utils.llm import llm
from config.settings import settings

MCP_BASE_URL = settings.MCP_SERVER_URL

def _call_mcp_get_assignments(learner_id: str) -> dict:
    """Call the MCP server tool directly via HTTP POST."""
    response = requests.post(
        f"{MCP_BASE_URL}/tools/get_assignments_for_learner",
        json={"learner_id": learner_id},
        timeout=10
    )
    response.raise_for_status()
    return response.json()

def assignment_agent(state: dict) -> dict:
    learner_id = state.get("learner_id", "unknown")
    # Step 1: Call MCP server to get assignment data
    try:
        mcp_result = _call_mcp_get_assignments(learner_id)
        assignment_data = mcp_result.get("assignments", [])
    except Exception as e:
        assignment_data = []
    # Step 2: Send data to LLM with the assignment_agent prompt
    prompt = load_prompt("assignment_agent")
    chain = prompt | llm
    response = chain.invoke({
        "learner_id": learner_id,
        "assignment_data": str(assignment_data) if assignment_data else "No assignments found."
    })
    # Step 3: Write to agent_response (the correct CoachState key)
    state["agent_response"] = response.content.strip()   
    state["execution_path"].append("assignment_agent")
    return state
