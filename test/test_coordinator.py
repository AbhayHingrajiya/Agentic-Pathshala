from agents.coordinator import coordinator_agent

state = {
    "messages": [
        type("obj", (object,), {
            "content": input("wrtie a query: ")
        })()
    ]
}

result = coordinator_agent(state)

print(result["current_intent"]) 