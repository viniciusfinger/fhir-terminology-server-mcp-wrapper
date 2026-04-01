import os
from pathlib import Path

from fastmcp import FastMCP
from fastmcp.server.providers import FileSystemProvider

from config import SERVER_NAME

provider = FileSystemProvider(
    root=Path(__file__).parent / "mcp",
    reload=os.getenv("MCP_ENV", "production") == "development",
)

mcp = FastMCP(SERVER_NAME, providers=[provider])

if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    port = int(os.getenv("MCP_PORT", "8000"))

    if transport == "http":
        mcp.run(transport="http", port=port)
    else:
        mcp.run(transport="stdio")
