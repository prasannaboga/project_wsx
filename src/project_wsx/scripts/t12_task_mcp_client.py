# src/project_wsx/scripts/t12_task_mcp_client.py
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main():
    async with streamablehttp_client("http://127.0.0.1:8002/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✅ MCP client initialized")
            tools = await session.list_tools()
            print("Available tools:", [t.name for t in tools.tools])

            result = await session.call_tool(
                "add_task",
                {"title": "Buy groceries", "due_date": "2025-08-28"},
            )

            print("Tool call result:", result)


if __name__ == "__main__":
    asyncio.run(main())
