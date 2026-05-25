import json
import re
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

    content = response.content.strip()
    
    # Try to parse content as JSON
    intent = "unknown"
    refactored_query = query
    
    try:
        # Strip any code block backticks if present
        json_str = content
        if json_str.startswith("```"):
            json_str = re.sub(r"^```(?:json)?\n", "", json_str)
            json_str = re.sub(r"\n```$", "", json_str)
        data = json.loads(json_str.strip())
        intent = data.get("intent", "unknown").strip().lower()
        refactored_query = data.get("refactored_query", query).strip()
    except Exception as e:
        # Fallback: if it's not valid JSON, treat the raw string (up to one line/short length) as intent
        cleaned_content = content.strip().lower()
        if "\n" not in cleaned_content and len(cleaned_content) < 50:
            intent = cleaned_content
        else:
            intent = "unknown"
        refactored_query = query

    state["current_intent"] = intent
    state["user_input"] = refactored_query
    
    state.setdefault("execution_path", [])
    state["execution_path"].append("coordinator_agent")
    return state

