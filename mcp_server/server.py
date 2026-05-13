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


if __name__ == "__main__":

    print("Starting MCP server...")

    mcp.run(
        transport="sse",
        host="0.0.0.0",
        port=8000
    )