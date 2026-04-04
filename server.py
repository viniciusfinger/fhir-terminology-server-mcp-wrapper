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
    port = int(os.getenv("PORT", "8000"))
    environment = os.getenv("ENVIRONMENT", "local")

    if environment == "production":
        mcp.run(transport="http", host="0.0.0.0", port=port)
    else:
        mcp.run(transport="stdio")
