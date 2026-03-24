from mcp.server.fastmcp import FastMCP
from project_wsx.core.settings import Settings

settings = Settings()


def create_mcp():
    mcp = FastMCP(
        "project_wsx_mcp_server",
        debug=settings.mcp_debug,
        json_response=True,
        log_level=settings.mcp_log_level,
        stateless_http=True,
        streamable_http_path="/",
    )

    return mcp
