from langgraph.graph import StateGraph, START, END
from .state import CoachState
from .node import coordinator_node, router_node, assignment_node, general_node, response_node, fallback_node
from .routes import route_intent

# -----------------------------
# BUILD GRAPH
# -----------------------------

builder = StateGraph(CoachState)

#Add nodes
builder.add_node("router", router_node)
builder.add_node("assignment", assignment_node)
builder.add_node("general", general_node)
builder.add_node("coordinator", coordinator_node)
builder.add_node("response", response_node)
builder.add_node("fallback", fallback_node)

#Add edges
builder.add_edge(START, "coordinator")
builder.add_edge("coordinator", "router")

#Add conditional edges
builder.add_conditional_edges(
    "router",
    route_intent,
    {
        "assignment": "assignment",
        "general": "general",
        "fallback": "fallback",
    }
)

# Response flow
builder.add_edge("assignment", "response")
builder.add_edge("general", "response")
builder.add_edge("fallback", "response")

builder.add_edge("response", END)

# Compile graph
graph = builder.compile()