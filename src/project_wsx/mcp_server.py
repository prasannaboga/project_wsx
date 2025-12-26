from mcp.server.fastmcp import FastMCP, Context

mcp_app = FastMCP(
    "mcp_server",
    host="127.0.0.1",
    port=8102,
    stateless_http=True,
    log_level="DEBUG",
    debug=True,
)


@mcp_app.tool()
def hello_world():
    return "Hello World!"


def main():
    mcp_app.run(transport="streamable-http")


if __name__ == "__main__":
    main()
