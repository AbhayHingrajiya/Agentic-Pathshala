from typing import TypedDict, Dict, List, Any

class CoachState(TypedDict):
    
    user_input: str
    currunt_intent: str
    tool_result: str
    retrieved_docs: List[str]
    final_response: str
    execution_path: List[str]

