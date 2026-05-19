from typing import TypedDict, Dict, List, Any, Optional

class CoachState(TypedDict):
    session: Dict[str, str]
    current_intent: str
    retrieved_context: str
    user_input: str
    learner_id: str
    agent_response: str
    execution_path: list
    momery_context: str
    assessment_mode: Optional[str]           
    assessment_assignment_id: Optional[str]  