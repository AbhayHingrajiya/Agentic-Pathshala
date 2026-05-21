from typing import Any

from orchestrator.graph import graph
from utils.logger import get_logger
from utils.chat_history_manager import ChatHistoryManager

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

        # Record the user message in history
        ChatHistoryManager.add_user_message(learner_id, user_input)

        # Build the message payload (including any running summary)
        api_messages = ChatHistoryManager.get_api_messages(learner_id)
        
        # Extract memory_context from the first system message if present
        memory_context = ""
        if api_messages and api_messages[0].get("role") == "system":
            memory_context = api_messages[0].get("content", "")
        
        # Attach the prepared messages and memory context to the state for downstream nodes
        state = {
            "user_input": user_input,
            "learner_id": learner_id,
            "session": session_data,
            "api_messages": api_messages,
            "messages": api_messages,  # new key for agents like general_agent
            "memory_context": memory_context,
            "execution_path": [],
            **extra_state    # passes assessment_mode, assessment_assignment_id, etc.
        }
        response = graph.invoke(state)
        # Record assistant reply for future summarisation
        from utils.chat_history_manager import ChatHistoryManager as CHM
        assistant_msg = response.get("agent_response", "")
        if assistant_msg:
            CHM.add_assistant_message(learner_id, assistant_msg)
        return response or {}

    def chat(self, user_input: str, learner_id: str, session: Any = None) -> dict[str, Any]:
        return self.invoke(user_input, learner_id, session)
