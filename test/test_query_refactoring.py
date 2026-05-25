import json
from agents.coordinator import coordinator_agent

# Test 1: Refactoring a query referring to "him" when history mentions "Abhay"
state_1 = {
    "user_input": "Show him assignment",
    "session": {"role": "coach"},
    "memory_context": "No past memories.",
    "messages": [
        {"role": "coach", "content": "I want to check on Abhay."},
        {"role": "assistant", "content": "Sure, what would you like to see about Abhay?"}
    ]
}

result_1 = coordinator_agent(state_1)
print("Test 1 - Input: Show him assignment")
print("Test 1 - Refactored Query:", result_1.get("user_input"))
print("Test 1 - Intent:", result_1.get("current_intent"))
print("-" * 40)

# Test 2: Refactoring "tell me about it" when history discusses RAG
state_2 = {
    "user_input": "tell me about it",
    "session": {"role": "learner"},
    "memory_context": "Learner is studying RAG.",
    "messages": [
        {"role": "learner", "content": "Is Retrieval-Augmented Generation (RAG) important?"},
        {"role": "assistant", "content": "Yes, RAG is extremely important for modern LLMs."}
    ]
}

result_2 = coordinator_agent(state_2)
print("Test 2 - Input: tell me about it")
print("Test 2 - Refactored Query:", result_2.get("user_input"))
print("Test 2 - Intent:", result_2.get("current_intent"))
print("-" * 40)
