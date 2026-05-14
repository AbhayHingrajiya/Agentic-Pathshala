import sys
from pathlib import Path

# Ensure project root is on sys.path so utils, config, etc. are importable
# regardless of how the server is launched (direct file or -m module).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastmcp import FastMCP
from utils.excel_store import read_records



mcp = FastMCP(
    name="AI Learning Coach MCP Server"
)


@mcp.tool()
def ping():

    return {
        "status": "working"
    }


@mcp.tool()
def get_learners():

    learners = read_records("learners.xlsx")

    return {
        "count": len(learners),
        "learners": learners
    }

@mcp.tool()
def get_assignments():

    assignments = read_records("assignments.xlsx")

    return {
        "count": len(assignments),
        "assignments": assignments
    }

@mcp.tool()
def get_assignments_for_learner(learner_id: str) -> dict:
    """Get all assignments for a specific learner."""
    all_assignments = read_records("assignments.xlsx")
    learner_assignments = [
        a for a in all_assignments
        if str(a.get("learner_id", "")).strip() == str(learner_id).strip()
    ]
    return {
        "learner_id": learner_id,
        "count": len(learner_assignments),
        "assignments": learner_assignments
    }


if __name__ == "__main__":

    print("Starting MCP server...")

    mcp.run(
        transport="sse",
        host="0.0.0.0",
        port=8000
    )