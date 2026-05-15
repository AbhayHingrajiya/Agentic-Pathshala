from utils.prompt_loader import load_prompt
from utils.llm import llm
from mcp_server.mcp_client import call_mcp_tool
from rag.retriever import retrieve_documents

def recommendation_agent(state: dict) -> dict:
    learner_id = state["learner_id"]
    user_query = state["user_input"]    
    # Step 1a: Fetch assignment data via MCP
    try:
        assignment_result = call_mcp_tool(
            "get_assignments_for_learner",
            {"learner_id": learner_id}
        )
        assignment_data = assignment_result.get("assignments", [])
    except Exception as e:
        assignment_data = []
        state["execution_path"].append(f"mcp_assignment_error: {str(e)}")
    # Step 1b: Fetch progress/score data via MCP
    try:
        progress_result = call_mcp_tool(
            "get_progress_for_learner",
            {"learner_id": learner_id}
        )
        progress_data = progress_result.get("progress", [])
    except Exception as e:
        progress_data = []
        state["execution_path"].append(f"mcp_progress_error: {str(e)}")
    # Step 1c: Retrieve relevant curriculum content via RAG
    # Uses the learner's own query to find relevant roadmap sections
    try:
        rag_results = retrieve_documents(user_query, k=3)
        # retrieve_documents returns list of (Document, score) tuples
        retrieved_context = "\n\n".join(
            doc.page_content for doc, _score in rag_results
        ) if rag_results else "No curriculum context found."
    except Exception as e:
        retrieved_context = "Curriculum context unavailable."
        state["execution_path"].append(f"rag_error: {str(e)}")
    # Step 2: Send all three inputs to LLM with recommendation prompt
    prompt = load_prompt("recommendation_agent")
    chain = prompt | llm
    response = chain.invoke({
        "learner_id": learner_id,
        "assignment_data": str(assignment_data) if assignment_data else "No assignments found.",
        "progress_data": str(progress_data) if progress_data else "No progress data found.",
        "retrieved_context": retrieved_context
    })
    # Step 3: Write to agent_response (the correct CoachState key)
    state["agent_response"] = response.content.strip()
    state["execution_path"].append("recommendation_agent")
    return state