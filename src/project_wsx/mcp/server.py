from mcp.server.fastmcp import FastMCP


def create_mcp():
    mcp = FastMCP(
        "project_wsx_mcp_server",
        stateless_http=True,
        json_response=True,
        log_level="DEBUG",
        debug=True
    )

    return mcp
