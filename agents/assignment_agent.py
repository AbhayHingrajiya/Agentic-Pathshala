from utils.prompt_loader import load_prompt
from utils.llm import llm
from mcp_server.mcp_client import call_mcp_tool
from langchain_core.prompts import PromptTemplate

def assignment_agent(state: dict) -> dict:
    learner_id = state.get("learner_id", "unknown")
    query = state.get("user_input", "")

    # Let the LLM decide which tool to call
    intent_prompt = PromptTemplate.from_template(
        "Analyze the following user query: '{query}'. "
        "Does the user want to see their PERSONAL assigned assignments, or the catalog of ALL AVAILABLE assignments? "
        "Respond with exactly 'personal' or 'all'."
    )
    classification = (intent_prompt | llm).invoke({"query": query}).content.strip().lower()
    
    try:
        if "all" in classification:
            result = call_mcp_tool("get_assignments", {})
            assignment_data = result.get("assignments", [])
            data_type = "All Available Assignments in Catalog"
        else:
            result = call_mcp_tool("get_assignments_for_learner", {"learner_id": learner_id})
            assignment_data = result.get("assignments", [])
            data_type = "Personal Assigned Assignments"
    except Exception as e:
        assignment_data = []
        data_type = "Error retrieving assignments"
        state.setdefault("execution_path", []).append(f"mcp_error: {str(e)}")

    prompt = load_prompt("assignment_agent")
    chain = prompt | llm

    response = chain.invoke({
        "learner_id": learner_id,
        "query": query,
        "data_type": data_type,
        "assignment_data": str(assignment_data) if assignment_data else "No assignments found.",
        "memory_context": state.get("memory_context", "No past memories.")
    })

    state["agent_response"] = response.content.strip()
    state.setdefault("execution_path", []).append(f"assignment_agent ({classification})")
    return state
