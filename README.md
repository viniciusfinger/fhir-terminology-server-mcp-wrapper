# FHIR Terminology Server MCP Wrapper

An MCP (Model Context Protocol) server that exposes operations of a FHIR terminology server to LLMs and AI applications.

## Prerequisites

- Python 3.10+

## Setup

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and adjust the variables:

```bash
cp .env.example .env
```

| Variable | Description | Default |
|---|---|---|
| `FHIR_TERMINOLOGY_SERVER_URL` | Base URL of the target FHIR terminology server | `https://tx.fhir.org/r4` |
| `MCP_SERVER_NAME` | MCP gateway display name | `FHIR Terminology Gateway` |
| `MCP_TRANSPORT` | Gateway transport (`stdio` or `http`) | `stdio` |
| `MCP_PORT` | Port for HTTP transport | `8000` |

## Run

```bash
# stdio (default for IDE integration)
python server.py

# HTTP
MCP_TRANSPORT=http python server.py

# FastMCP CLI
fastmcp run server.py:mcp
```
