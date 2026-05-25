# pyrefly: ignore [missing-import]
from langgraph.graph import StateGraph, START, END
from .state import CoachState
from .node import (
    coordinator_node, 
    notes_agent_node, 
    assessment_agent_node, 
    evaluator_agent_node, 
    response_node, 
    fallback_node, 
    general_agent_node,
    assignment_node, 
    recommendation_node,
    coach_assignment_node,
    memory_reader_node, 
    memory_writer_node,
    progress_agent_node
)
from .routes import route_intent

# -----------------------------
# BUILD GRAPH
# -----------------------------

builder = StateGraph(CoachState)

builder.add_node("coordinator", coordinator_node)
builder.add_node("notes_agent", notes_agent_node)
builder.add_node("assessment_agent", assessment_agent_node)
builder.add_node("evaluator_agent", evaluator_agent_node)
builder.add_node("response", response_node)
builder.add_node("fallback", fallback_node)
builder.add_node("general_agent", general_agent_node)
builder.add_node("assignment", assignment_node)
builder.add_node("recommendation", recommendation_node)
builder.add_node("coach_assignment", coach_assignment_node)
builder.add_node("memory_reader", memory_reader_node)
builder.add_node("memory_writer", memory_writer_node)
builder.add_node("progress_agent", progress_agent_node)

# 2. Start edge
builder.add_edge(START, "memory_reader")                
builder.add_edge("memory_reader", "coordinator") 

builder.add_conditional_edges(
    "coordinator",
    route_intent,
    {
        "notes_agent": "notes_agent",
        "assignment": "assignment",
        "progress_agent": "progress_agent",
        "assessment_agent": "assessment_agent",
        "recommendation": "recommendation",  
        "evaluator_agent": "evaluator_agent",
        "fallback": "general_agent",
        "coach_assignment": "coach_assignment"
    }
)

builder.add_edge("notes_agent", "response")
builder.add_edge("assessment_agent", "response")
builder.add_edge("recommendation", "response") 
builder.add_edge("evaluator_agent", "response")
builder.add_edge("fallback", "response")
builder.add_edge("general_agent", "response")
builder.add_edge("assignment", "response")
builder.add_edge("coach_assignment", "response")
builder.add_edge("progress_agent", "response")

builder.add_edge("response", "memory_writer")    
builder.add_edge("memory_writer", END)   

# Compile graph
graph = builder.compile()
