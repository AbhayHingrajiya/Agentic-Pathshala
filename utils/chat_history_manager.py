import threading
from typing import List, Dict, Any

# Removed unused import


class ChatHistoryManager:

    _lock = threading.Lock()
    _store: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def _ensure_learner(cls, learner_id: str) -> Dict[str, Any]:
        if learner_id not in cls._store:
            cls._store[learner_id] = {
                "messages": [],  # List[{'role': str, 'content': str}]
                "summary": "",
                "summary_up_to_index": 0,
            }
        return cls._store[learner_id]

    @classmethod
    def add_user_message(cls, learner_id: str, content: str) -> None:
        with cls._lock:
            data = cls._ensure_learner(learner_id)
            data["messages"].append({"role": "user", "content": content})

    @classmethod
    def add_assistant_message(cls, learner_id: str, content: str) -> None:
        with cls._lock:
            data = cls._ensure_learner(learner_id)
            data["messages"].append({"role": "assistant", "content": content})

    @classmethod
    def _generate_summary(cls, prior_summary: str, messages_to_summarize: List[Dict[str, str]]) -> str:
        """Placeholder summarisation – replace with real LLM call.
        For now we simply concatenate messages; the production version should
        invoke an LLM with a prompt similar to the one in the markdown.
        """
        # Build a simple textual representation
        parts = []
        if prior_summary:
            parts.append(f"Previous summary:\n{prior_summary}\n\n")
        parts.append("New messages:\n")
        for m in messages_to_summarize:
            role = "User" if m["role"] == "user" else "Assistant"
            parts.append(f"{role}: {m['content']}\n")
        # In a real implementation this would be sent to an LLM.
        # Here we just truncate to a reasonable length.
        return " ".join(parts)[:1000]

    @classmethod
    def get_api_messages(cls, learner_id: str, window_size: int = 5) -> List[Dict[str, str]]:
        """Construct the message list to send to the LLM, applying the sliding‑window logic.
        Returns a list of dicts ``{"role": ..., "content": ...}``.
        """
        with cls._lock:
            data = cls._ensure_learner(learner_id)
            all_messages = data["messages"]
            prior_summary = data.get("summary", "")
            summarized_up_to = data.get("summary_up_to_index", 0)

            recent = all_messages[summarized_up_to:]
            user_indices = [i for i, m in enumerate(recent) if m["role"] == "user"]

            if len(user_indices) > window_size:
                cutoff_local = user_indices[-window_size]
                to_summarize = recent[:cutoff_local]
                recent = recent[cutoff_local:]

                new_summary = cls._generate_summary(prior_summary, to_summarize)
                data["summary"] = new_summary
                data["summary_up_to_index"] = summarized_up_to + cutoff_local
                prior_summary = new_summary

            api_messages: List[Dict[str, str]] = []
            if prior_summary:
                api_messages.append({"role": "system", "content": f"Summary of earlier conversation:\n{prior_summary}"})
            api_messages.extend([{"role": m["role"], "content": m["content"]} for m in recent])
            return api_messages
    @classmethod
    def reset(cls) -> None:
        """Clear all stored chat histories – useful for testing or session reset."""
        with cls._lock:
            cls._store.clear()

# Export the manager for easy import
__all__ = ["ChatHistoryManager"]

