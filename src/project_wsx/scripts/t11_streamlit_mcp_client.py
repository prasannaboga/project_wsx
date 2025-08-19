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

    for resource in resources_response.resources:
        display_name = get_display_name(resource)
        print(f"Resource: {display_name} ({resource.uri})")

    templates_response = await session.list_resource_templates()
    for template in templates_response.resourceTemplates:
        display_name = get_display_name(template)
        print(f"Resource Template: {display_name}")


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


asyncio.run(get_my_mcp_details())
