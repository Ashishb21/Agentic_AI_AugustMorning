## create a mcp client that can call the get_current_time tool from mcp-server.py


import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient  
from langchain.agents import create_agent
from langchain_ollama import ChatOllama

async def main():
    client = MultiServerMCPClient(  
        {
            "my-mcp": {
                "transport": "stdio",  # Local subprocess communication
                "command": "uv",
                # Absolute path to your mcp-server.py file
                "args": ["run", "python", "/Users/ashishbansal/Documents/Training/AiStack/Aistack_Course/Project_1/6.MCP/mcp-server.py"],
            },
            # "weather": {
            #     "transport": "http",  # HTTP-based remote server
            #     # Ensure you start your weather server on port 8000
            #     "url": "http://localhost:8000/mcp",
            # }
        }
    )

    tools = await client.get_tools()  


    ### LLM setup###

    llm = ChatOllama(
    model="llama3.2",
    base_url="http://localhost:11434"
)

    agent = create_agent(
        llm,
        tools=tools,
        system_prompt="You are a helpful assistant that uses tools when needed",
        debug=False
    )

    user_query = "What is the current time?"

    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": user_query}]}
    )
    
    print(response["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())