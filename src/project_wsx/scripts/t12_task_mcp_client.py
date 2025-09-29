import asyncio
import time
from datetime import datetime
import traceback
import streamlit as st
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


MCP_SERVER_URL = "http://127.0.0.1:8002/mcp"


class MCPClient:
    def __init__(self, url=MCP_SERVER_URL):
        self.url = url
        self.session = None
        self.client = None

    async def connect(self):
        if self.session:
            return self.session

        self.client = await streamablehttp_client(self.url)
        read_stream, write_stream, _ = self.client
        self.session = ClientSession(read_stream, write_stream)
        await self.session.initialize()
        return self.session

    async def call_tool(self, tool_name: str, args: dict):
        session = await self.connect()
        result = await session.call_tool(tool_name, args)

        if result.structuredContent:
            return result.structuredContent
        return {"text": result.content[0].text}

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None


@st.cache_resource
def get_mcp_client():
    return MCPClient()


async def call_add_task(title: str, due_date: str) -> str:
    """Call the add_task tool on the MCP server."""
    try:
        client = get_mcp_client()
        return await client.call_tool(
            "add_task", {"title": title, "due_date": due_date}
        )
    except Exception as e:
        st.error(traceback.format_exc())
        return f"Error: {str(e)}"


def main():
    st.title("MCP Task Manager")
    st.subheader("Add a New Task")

    task_title = st.text_input("Task Title", placeholder="Enter task title")
    due_date = st.date_input("Due Date", min_value=datetime.today())
    due_date_str = due_date.strftime("%Y-%m-%d")

    if st.button("Add Task"):
        if not task_title:
            st.error("Task title is required.")
            return

        with st.spinner("Adding task..."):
            time.sleep(2)
            result = asyncio.run(call_add_task(task_title, due_date_str))
            if "Error" in result:
                st.error(result)
            else:
                st.success(result)


if __name__ == "__main__":
    main()
