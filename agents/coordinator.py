from utils.prompt_loader import load_prompt
from utils.llm import llm

def coordinator_agent(state):
    query = state["messages"][-1].content
    prompt = load_prompt("coordinator")
    chain = prompt | llm
    response = chain.invoke({"query": query})
    
    state["current_intent"] = response.content.strip()
    
    return state

