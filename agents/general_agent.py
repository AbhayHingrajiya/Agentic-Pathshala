import logging
from utils import load_prompt, llm

logger = logging.getLogger(__name__)

def general_agent(state):
    # Retrieve the current user query
    query = state["user_input"]
    logger.info("Executing general_agent for query: %s", query)

    # Grab the full chat history (list of dicts) if available
    messages = state.get("messages", [])
    # Convert the list of messages into a readable string for the prompt
    # Each message is formatted as "Role: content"
    history_str = "\n".join([f"{msg.get('role', 'learner').title()}: {msg.get('content', '')}" for msg in messages])

    # Load the base prompt template (which expects {memory_context} and {query})
    base_prompt = load_prompt("general_agent")
    # Create a combined prompt that includes the full history before the current query
    # We'll feed the history as the memory_context variable
    chain = base_prompt | llm

    combined_context = """{mem}\n\nChat History:\n{hist}""".format(
        mem=state.get("memory_context", "No past memories."),
        hist=history_str if history_str else "No prior chat."
    )
    response = chain.invoke({
        "query": query,
        "memory_context": combined_context
    })

    # Store the response back into state
    state["agent_response"] = response.content.strip()
    # Ensure execution_path is tracked (list may already exist)
    if "execution_path" not in state:
        state["execution_path"] = []
    state["execution_path"].append("general_agent")
    return state
