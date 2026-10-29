from langchain_core.tools import tool
from langchain.agents import create_agent
from datetime import datetime
from fastmcp import FastMCP

mcp=FastMCP("my-mcp")

@mcp.tool()
def get_current_time() -> str:
    "Return the current time in format YYYY-MM-DD HH:MM:SS"
    print("Tool get_current_time called")
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    
    mcp.run(transport="stdio")
    ## if you want to run using htttp transport, use below code instead of above line
    # mcp.run(transport="http", host="localhost", port=8000,path="/mcp")
    # command to run uv run mcp-server.py