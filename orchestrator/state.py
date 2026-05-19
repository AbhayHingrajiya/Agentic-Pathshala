from typing import TypedDict, Dict

class CoachState(TypedDict):
    session: Dict[str, str]
    current_intent: str
    retrieved_context: str
    user_input: str
    learner_id: str
    agent_response: str
    execution_path: list
    momery_context: str