from utils.prompt_loader import load_prompt
from utils.llm import llm

def coordinator_agent(state):
    query = state["user_input"]
    session = state.get("session", {})
    role = session.get("role", "learner")

    prompt = load_prompt("coordinator")
    chain = prompt | llm
    response = chain.invoke({"query": query, "role": role})
    
    state["current_intent"] = response.content.strip().lower()
    state["execution_path"].append("coordinator_agent")
    
    return state
