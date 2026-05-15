# pyrefly: ignore [missing-import]
from langgraph.graph import StateGraph, START, END
from .state import CoachState
from .node import coordinator_node, notes_agent_node, assessment_agent_node, response_node, fallback_node
from .routes import route_intent

# -----------------------------
# BUILD GRAPH
# -----------------------------

builder = StateGraph(CoachState)

builder.add_node("coordinator", coordinator_node)
builder.add_node("notes_agent", notes_agent_node)
builder.add_node("assessment_agent", assessment_agent_node)
builder.add_node("response", response_node)
builder.add_node("fallback", fallback_node)

# 2. Start edge
builder.add_edge(START, "coordinator")

builder.add_conditional_edges(
    "coordinator",
    route_intent,
    {
        "notes_agent": "notes_agent",
        "assessment_agent": "assessment_agent",
        "fallback": "fallback",
    }
)

builder.add_edge("notes_agent", "response")
builder.add_edge("assessment_agent", "response")
builder.add_edge("fallback", "response")

builder.add_edge("response", END)

# Compile graph
graph = builder.compile()
