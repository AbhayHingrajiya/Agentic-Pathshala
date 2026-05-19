import logging
from utils import load_prompt, llm

logger = logging.getLogger(__name__)

def general_agent(state):
    query = state["user_input"]
    logger.info("Executing general_agent for query: %s", query)
    
    prompt = load_prompt("general_agent")
    chain = prompt | llm
    
    response = chain.invoke({
        "query": query,
        "memory_context": state.get("memory_context", "No past memories.")
    })
    
    state["agent_response"] = response.content.strip()
    state["execution_path"].append("general_agent")
    
    return state
