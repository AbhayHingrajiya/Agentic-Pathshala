from utils import load_prompt
from utils import llm

def coordinator_agent(state):
    query = state["user_input"]
    prompt = load_prompt("coordinator")
    chain = prompt | llm
    response = chain.invoke({"query": query})
    
    state["current_intent"] = response.content.strip()
    state["execution_path"].append("coordinator_agent")
    
    return state

