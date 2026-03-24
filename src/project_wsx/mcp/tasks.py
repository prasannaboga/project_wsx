from mcp.server.fastmcp import Context

def register(mcp):
    @mcp.tool()
    def add_numbers(a: int, b: int) -> int:
        return a + b

    @mcp.tool()
    def multiply_numbers(a: int, b: int) -> int:
        return a * b
