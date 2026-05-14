from typing import TypedDict

class CoachState(TypedDict):

    current_intent: str
    retrieved_context: str
    user_input: str
    learner_id: str
    agent_response: str
    execution_path: list