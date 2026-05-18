def route_intent(state):
    intent = state.get("current_intent")
    session = state.get("session", {})
    role = session.get("role", "learner")

    # Strict RBAC Guard Gateway: Block unauthorized role access to coach operations
    if intent in ["assign_task", "track_progress"] and role != "coach":
        return "fallback"

    # Coach Fallback Gate: If a coach triggers learner checking intents, redirect to coach administrative handler
    if role == "coach" and intent in ["assignment_query", "progress_query"]:
        return "coach_assignment"

    routes = {
        "assignment_query": "assignment", 
        "progress_query": "progress_agent",
        "recommendation": "recommendation",
        "evaluation_request": "evaluation_agent",
        "notes_query": "notes_agent",
        "assessment_query": "assessment_agent",
        "evaluator_query": "evaluator_agent",
        "assign_task": "coach_assignment"
    }

    return routes.get(intent, "fallback")
