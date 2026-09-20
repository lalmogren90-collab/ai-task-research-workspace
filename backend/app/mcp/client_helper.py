import asyncio
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


PROJECT_ROOT = Path(__file__).resolve().parents[3]


async def _call_mcp_tool(
    tool_name: str,
    arguments: dict | None = None,
):
    server_params = StdioServerParameters(
        command="mcp",
        args=[
            "run",
            "backend/app/mcp/server.py",
        ],
        cwd=str(PROJECT_ROOT),
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                tool_name,
                arguments=arguments or {},
            )

            if result.is_error:
                return {
                    "error": "MCP tool execution failed.",
                    "content": [
                        item.text
                        for item in result.content
                        if hasattr(item, "text")
                    ],
                }

            if result.structured_content is not None:
                return result.structured_content

            return {
                "content": [
                    item.text
                    for item in result.content
                    if hasattr(item, "text")
                ]
            }


def call_mcp_tool(
    tool_name: str,
    arguments: dict | None = None,
):
    return asyncio.run(
        _call_mcp_tool(
            tool_name,
            arguments,
        )
    )
