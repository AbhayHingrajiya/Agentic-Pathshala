import json
from agents.general_agent import general_agent
state = {
    'user_input': 'What is the capital of Gujarat?',
    'memory_context': 'Learner likes history.',
    'messages': [
        {'role': 'learner', 'content': 'Who are you?'},
        {'role': 'assistant', 'content': 'I am AI.'}
    ]
}
result = general_agent(state)
print(result.get('agent_response', ''))
