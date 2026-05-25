import json
from agents.coordinator import coordinator_agent

state = {
    "user_input": "What can you do?",
    "memory_context": "Learner is curious about AI.",
    "messages": [
        {"role": "learner", "content": "Tell me about the system."},
        {"role": "assistant", "content": "I can help you with many tasks."}
    ]
}

result_state = coordinator_agent(state)
print("Intent:", result_state.get("current_intent"))
