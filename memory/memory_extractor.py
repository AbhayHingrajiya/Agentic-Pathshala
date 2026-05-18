import ast 
import logging
from utils.prompt_loader import load_prompt
from utils.llm import llm

logger = logging.getLogger(__name__)

def extract_memories(learner_id: str, user_input: str, agent_response: str) -> list[str]:
    """
    Uses the LLM to extract memorable facts from a conversation exchange.
    Returns a list of memory strings. May return [] if nothing important happened.
    Why ast.literal_eval?
    The LLM returns a Python list as a string: '["fact1", "fact2"]'
    ast.literal_eval safely converts this string to an actual Python list.
    We never use eval() because that would be a security risk.
    """
    try:
        prompt = load_prompt("memory_extractor")
        chain = prompt | llm
        result = chain.invoke({
            "learner_id": learner_id,
            "user_input": user_input,
            "agent_response": agent_response,
        })
        raw_text = result.content.strip()
        logger.debug("Memory extractor raw output: %s", raw_text)
        # Parse the Python list the LLM returned
        memories = ast.literal_eval(raw_text)
        # Validate: must be a list of strings
        if not isinstance(memories, list):
            return []
        return [m for m in memories if isinstance(m, str) and m.strip()]
    except Exception as e:
        logger.warning("Memory extraction failed: %s", str(e))
        return []   # Safe fallback — never crash the main flow