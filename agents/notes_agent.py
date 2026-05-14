from utils import load_prompt, llm
from rag import retrieve_documents

def notes_agent(state):
    query = state["user_input"]
    
    results = retrieve_documents(query, k=5)
    
    context = "\n\n".join([doc.page_content for doc, score in results])
    
    prompt = load_prompt("notes_agent")
    chain = prompt | llm
    
    response = chain.invoke({
        "context": context,
        "query": query
    })
    
    state["agent_response"] = response.content
    state["retrieved_context"] = context
    state["execution_path"].append("notes_agent")
    
    return state
