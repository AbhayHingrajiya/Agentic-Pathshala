from typing import TypedDict

class CoachState(TypedDict):

    messages: list
    user_role: str
    learner_id: str
    current_intent: str
    retrieved_context: str
    tool_results: dict
    requires_approval: bool
    final_response: str