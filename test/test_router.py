from orchestrator.routes import route_intent

state = {
    "current_intent": "recommendation"
}

result = route_intent(state)

print(result)