# pyrefly: ignore [missing-import]
from langchain.tools import tool

# @tool
# async def get_assignment_status_tool(
#     learner_id: str,
#     assignment_id: str
# ):
#     pass\

@tool
async def get_assignment_status_tool(
    learner_id: str,
    assignment_id: str
):

    return {
        "status": "submitted",
        "score": 85
    }