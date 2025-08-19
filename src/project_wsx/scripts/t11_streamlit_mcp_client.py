import asyncio

import requests
import streamlit as st
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.shared.metadata_utils import get_display_name

st.set_page_config(page_title="Mcp Client")
st.title("Mcp Client")

MCP_SERVER_URL = "http://localhost:8001/mcp"


async def display_mcp_tools(session: ClientSession):
    tools_response = await session.list_tools()

    with st.expander("See Tools"):
        for tool in tools_response.tools:
            st.json(tool)


async def display_mcp_resources(session: ClientSession):
    resources_response = await session.list_resources()

    with st.expander("See Resources"):
        for resource in resources_response.resources:
            st.json(resource)

        templates_response = await session.list_resource_templates()
        for template in templates_response.resourceTemplates:
            st.json(template)

async def display_mcp_prompts(session: ClientSession):
    prompts_response = await session.list_prompts()

    with st.expander("See Prompts"):
        for prompt in prompts_response.prompts:
            st.json(prompt)

async def get_my_mcp_details():
    async with streamablehttp_client(MCP_SERVER_URL) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            await display_mcp_tools(session)
            await display_mcp_resources(session)
            await display_mcp_prompts(session)


asyncio.run(get_my_mcp_details())
