import json
import re
from utils.prompt_loader import load_prompt
from utils.llm import llm
from rag import retrieve_documents
from mcp_server.mcp_client import call_mcp_tool


def assessment_agent(state: dict) -> dict:
    """
    Dispatcher: routes to the correct sub-mode based on state["assessment_mode"].
      - "fetch_questions"  → verify assignment + retrieve questions+correct_answers from RAG
      - "evaluate_answer"  → LLM semantically scores one question/answer pair
    """
    mode = state.get("assessment_mode", "fetch_questions")

    if mode == "fetch_questions":
        return _fetch_questions(state)
    elif mode == "evaluate_answer":
        return _evaluate_single_answer(state)
    else:
        state["agent_response"] = json.dumps({"error": f"Unknown assessment mode: {mode}"})
        return state


def _fuzzy_match(user_text: str, assignment_ids: list[str]) -> str | None:
    """
    Match user text against a list of assignment_id strings
    (which ARE the full titles, e.g. "Assignment 1: Python Mastery & OOP").

    Priority:
    1. Exact match
    2. Full assignment_id is a substring of user text
    3. Assignment number match: "assignment 1" in user text matches "Assignment 1: ..."
    """
    user_lower = user_text.lower()

    # 1. Exact
    for aid in assignment_ids:
        if aid.lower() == user_lower:
            return aid

    # 2. Full ID substring in user text
    for aid in assignment_ids:
        if aid.lower() in user_lower:
            return aid

    # 3. Number-based: user says "assignment 3" → find "Assignment 3: ..."
    if "assignment" in user_lower:
        input_nums = re.findall(r'\d+', user_lower)
        if input_nums:
            # Prefer exact number match first (e.g. "3" before "13", "14")
            for num in input_nums:
                for aid in assignment_ids:
                    title_nums = re.findall(r'\d+', aid)
                    if title_nums and title_nums[0] == num:   # first number in title must match
                        return aid

    return None


def _fetch_questions(state: dict) -> dict:
    """
    1. Get learner's assigned assignments via MCP.
    2. Resolve which assignment the user wants (from state or user_input).
    3. If unclear, ask the user to specify.
    4. Retrieve questions + correct answers from RAG using the assignment id/title.
    5. Return structured JSON in agent_response.
    """
    learner_id = state.get("learner_id", "")
    explicit_assignment_id = state.get("assessment_assignment_id", "").strip()
    user_input = state.get("user_input", "")

    # --- MCP: Get learner's assigned assignments ---
    # NOTE: In this system, assignment_id IS the full human-readable title
    # e.g. "Assignment 1: Python Mastery & OOP"
    try:
        result = call_mcp_tool("get_assignments_for_learner", {"learner_id": learner_id})
        learner_assignment_ids = [
            a["assignment_id"].strip()
            for a in result.get("assignments", [])
        ]
    except Exception as e:
        state["agent_response"] = json.dumps(
            {"error": f"Could not verify assignments: {str(e)}"}
        )
        state["execution_path"].append("assessment_agent:mcp_error")
        return state

    if not learner_assignment_ids:
        state["agent_response"] = (
            "You don't have any assignments assigned to you yet. "
            "Please contact your coach to get assignments."
        )
        state["execution_path"].append("assessment_agent:no_assignments")
        return state

    # --- Resolve the target assignment ---
    # Priority: explicit state field > fuzzy match from user_input
    resolved_id = None

    if explicit_assignment_id:
        resolved_id = _fuzzy_match(explicit_assignment_id, learner_assignment_ids)

    if not resolved_id:
        resolved_id = _fuzzy_match(user_input, learner_assignment_ids)

    if not resolved_id:
        # Cannot identify the assignment → ask the user to specify
        titles_str = "\n".join(f"  • {aid}" for aid in sorted(learner_assignment_ids))
        state["agent_response"] = (
            "Sure! I'd love to start your assessment. "
            "Which assignment would you like to be assessed on?\n\n"
            f"Your assigned assignments:\n{titles_str}\n\n"
            "Please type something like: 'take my assessment of Assignment 1: Python Mastery & OOP'"
        )
        state["execution_path"].append("assessment_agent:ask_assignment")
        return state

    # --- RAG: Fetch questions + correct answers ---
    # Query with the full assignment id (which is also the document title)
    results = retrieve_documents(resolved_id, k=100)
    context = "\n\n".join([doc.page_content for doc, score in results])

    if not context.strip():
        state["agent_response"] = json.dumps(
            {"error": f"No learning materials found for '{resolved_id}'. Please contact your coach."}
        )
        state["execution_path"].append("assessment_agent:no_context")
        return state

    prompt = load_prompt("assessment_fetch_questions")
    chain = prompt | llm
    response = chain.invoke({
        "context": context,
        "assignment_id": resolved_id
    })

    state["agent_response"] = response.content.strip()
    state["retrieved_context"] = context
    state["execution_path"].append("assessment_agent:fetch_questions")
    return state


def _evaluate_single_answer(state: dict) -> dict:
    """
    Semantically evaluates one question/answer pair.
    state["user_input"] must be a JSON string:
        {"question": "...", "correct_answer": "...", "user_answer": "..."}
    Returns JSON: {"score": int, "max_score": 5, "reason": str}
    """
    payload = state.get("user_input", "{}")

    prompt = load_prompt("assessment_evaluate_answer")
    chain = prompt | llm
    response = chain.invoke({"payload": payload})

    state["agent_response"] = response.content.strip()
    state["execution_path"].append("assessment_agent:evaluate_answer")
    return state