from typing import Any

from orchestrator.graph import graph
from utils.logger import get_logger

logger = get_logger(__name__)


class AIService:
    def __init__(self) -> None:
        self._logger = logger

    def invoke(self, user_input: str, learner_id: str, session: Any = None, **extra_state) -> dict[str, Any]:
        session_data = {}
        if session:
            if hasattr(session, "role"):
                session_data = {
                    "user_id": session.user_id,
                    "role": session.role,
                    "name": session.name,
                    "email": session.email
                }
            elif isinstance(session, dict):
                session_data = session

        state = {
            "user_input": user_input,
            "learner_id": learner_id,
            "session": session_data,
            "execution_path": [],
            **extra_state    # passes assessment_mode, assessment_assignment_id, etc.
        }
        response = graph.invoke(state)
        return response or {}

    def chat(self, user_input: str, learner_id: str, session: Any = None) -> dict[str, Any]:
        return self.invoke(user_input, learner_id, session)
