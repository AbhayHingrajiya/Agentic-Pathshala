from utils.prompt_loader import load_prompt
from utils.llm import llm
from mcp_server.mcp_client import call_mcp_tool


def assignment_agent(state: dict) -> dict:
    learner_id = state.get("learner_id", "unknown")

    # Step 1: Call MCP server tool to get assignment data
    try:
        result = call_mcp_tool(
            "get_assignments_for_learner",
            {"learner_id": learner_id}
        )
        assignment_data = result.get("assignments", [])
    except Exception as e:
        assignment_data = []
        state["execution_path"].append(f"mcp_error: {str(e)}")

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
