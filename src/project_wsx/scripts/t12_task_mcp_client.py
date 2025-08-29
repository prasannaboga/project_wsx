import asyncio
import time
from datetime import datetime

import streamlit as st
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def call_add_task(title: str, due_date: str) -> str:
    """Call the add_task tool on the MCP server."""
    try:
        async with streamablehttp_client("http://127.0.0.1:8002/mcp") as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.call_tool(
                    "add_task", {"title": title, "due_date": due_date}
                )
                return result.structuredContent.get("result", str(str(result.content[0].text)))  
    except Exception as e:
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
