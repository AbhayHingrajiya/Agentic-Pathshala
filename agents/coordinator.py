from utils.prompt_loader import load_prompt
from utils.llm import llm

def coordinator_agent(state):
    query = state["user_input"]
    session = state.get("session", {})
    role = session.get("role", "learner")

    prompt = load_prompt("coordinator")
    chain = prompt | llm

    # Build chat history string
    messages = state.get("messages", [])
    history_str = "\n".join([f"{msg.get('role', 'learner').title()}: {msg.get('content', '')}" for msg in messages])
    combined_context = f"{state.get('memory_context', 'No past memories.')}\n\nChat History:\n{history_str if history_str else 'No prior chat.'}"

    response = chain.invoke({
        "query": query,
        "role": role,
        "memory_context": combined_context
    })

    state["current_intent"] = response.content.strip().lower()
    state.setdefault("execution_path", [])
    state["execution_path"].append("coordinator_agent")
    return state
