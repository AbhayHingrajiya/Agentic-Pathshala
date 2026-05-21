from typing import TypedDict, Dict, List, Optional

class CoachState(TypedDict, total=False):
    session: Dict[str, str]
    current_intent: str
    retrieved_context: str
    user_input: str
    learner_id: str
    agent_response: str
    execution_path: List[str]
    memory_context: str
    assessment_mode: Optional[str]
    assessment_assignment_id: Optional[str]
    messages: List[Dict[str, str]]