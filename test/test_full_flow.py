from orchestrator.graph import graph

state = {

    "messages": [
        {
            "role": "user",
            "content": "hello how are you?"
        }
    ],

    "current_intent": "",

    "final_response": ""
}

result = graph.invoke(state)

print("\nFINAL RESULT:\n")
print(result)