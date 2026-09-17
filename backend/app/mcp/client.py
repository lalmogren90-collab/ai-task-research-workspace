import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server_params = StdioServerParameters(
        command="mcp",
        args=[
            "run",
            "backend/app/mcp/server.py",
        ],
        cwd="/Users/cysec/Desktop/AI Training",
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()

            print("Available MCP tools:")

            for tool in tools.tools:
                print(f"- {tool.name}")

            print("\nCalling get_tasks...")

            result = await session.call_tool(
                "get_tasks",
                arguments={},
            )

            print("\nMCP result:")
            print(result)


if __name__ == "__main__":
    asyncio.run(main())