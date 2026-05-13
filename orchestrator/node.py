from .state import CoachState

# -----------------------------
# NODE FUNCTIONS
# -----------------------------

def coordinator_node(state: CoachState) -> CoachState:
    try:
        path = state.get("execution_path", [])
        path.append("coordinator")
        return {"execution_path": path}
    except Exception as e:
        return {
            "tool_result": {
                "status": "error",
                "message": str(e),
                "source": "coordinator_node"
            }
        }

def router_node(state: CoachState) -> dict[str, str]:
    try:
        path = state.get("execution_path", [])
        path.append("router")
        query = state["user_input"].lower()

        if "assignment" in query:
            intent = "assignment"
        elif "hello" in query:
            intent = "general"
        else:
            intent = 'fallback'

        return {"currunt_intent": intent, "execution_path": path}
    except Exception as e:
        return {
            "tool_result": {
                "status": "error",
                "message": str(e),
                "source": "router_node"
            }
        }

def assignment_node(state: CoachState) -> dict[str, str]:
    try:
        path = state.get("execution_path", [])
        path.append("assignment")
        return {
            "tool_result": {
                "status": "success",
                "message": "Assignment feature coming soon.",
                "source": "assignment_node"
            },
            "execution_path": path
        }
    except Exception as e:
        return {
            "tool_result": {
                "status": "error",
                "message": str(e),
                "source": "assignment_node"
            }
        }

def general_node(state: CoachState) -> dict[str, str]:
    try:
        path = state.get("execution_path", [])
        path.append("general")
        return {
            "tool_result": {
                "status": "success",
                "message": f"You said: {state['user_input']}",
                "source": "general_node"
            },
            "execution_path": path
        }
    except Exception as e:
        return {
            "tool_result": {
                "status": "error",
                "message": str(e),
                "source": "general_node"
            }
        }
    
def response_node(state: CoachState) -> dict[str, str]:
    try:
        path = state.get("execution_path", [])
        path.append("response")
        tool_result = state["tool_result"]

        if tool_result["status"] == "success":
            message = tool_result["message"]
        else:
            message = "Something went wrong."

        return {"tool_result": message, "execution_path": path}
    except Exception as e:
        return {
            "tool_result": {
                "status": "error",
                "message": str(e),
                "source": "response_node"
            }
        }

def fallback_node(state: CoachState) -> dict[str, str]:
    try:
        path = state.get("execution_path", [])
        path.append("fallback")
        return {
            "tool_result": {
                "status": "error",
                "message": "I don't understand your request.",
                "source": "fallback_node"
            },
            "execution_path": path
        }
    except Exception as e:
        return {
            "tool_result": {
                "status": "error",
                "message": str(e),
                "source": "fallback_node"
            }
        }