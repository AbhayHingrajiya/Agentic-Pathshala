def route_intent(state):

    intent = state.get("current_intent")

    routes = {
        "assignment_query": "assignment", 
        "progress_query": "progress_agent",
        "recommendation": "recommendation_agent",
        "evaluation_request": "evaluation_agent",
        "notes_query": "notes_agent",
        "assessment_query": "assessment_agent"
    }

    return routes.get(intent, "fallback")

