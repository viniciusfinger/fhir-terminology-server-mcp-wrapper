# FHIR Terminology MCP Wrapper

<p align="center">
  <img src="logo.png" alt="Model Context Protocol (MCP) plus HL7 FHIR" width="480" />
</p>

## Overview

This project is an **MCP (Model Context Protocol) wrapper**: it turns standard FHIR **Terminology Services** operations into **tools** that LLMs and AI assistants can call safely and predictably.

It is **not** a terminology server. It does not store code systems or ValueSets. It **forwards** requests to a real FHIR terminology backend (for example the public `tx.fhir.org`, or your own HAPI FHIR, Ontoserver, or vendor TS endpoint) and returns normalized results to the client.

### Why use it?

- **Familiar interface for AI applications** — Any MCP-compatible host (Claude Desktop, custom agents or other MCP servers) can resolve clinical codes without hard-coding HTTP clients or FHIR URLs in the prompt.
- **Reuse your existing stack** — Point `FHIR_TERMINOLOGY_SERVER_URL` at the same server your EHR or integration layer already uses; no duplicate terminology store.
- **Structured, typed calls** — Tools expose parameters such as `system` and `code` instead of asking the model to craft raw `$lookup` URLs.
- **Separation of concerns** — Clinical vocabulary stays on the authoritative TS; this repo only bridges MCP ↔ FHIR.

### What you can do with it

- **Resolve codes to human-readable labels** — e.g. SNOMED CT, LOINC, ICD (depending on what the backend supports), for documentation, support bots, or developer copilots.
- **Ground answers in authoritative terminology** — Assistants can call `lookup_code` to verify a code and display string before suggesting documentation or code.
- **Swap backends** — Use the public terminology service for demos, or a private endpoint for restricted or local code systems.

Today the wrapper exposes **`lookup_code`** (`CodeSystem/$lookup`). Additional tools (e.g. `$validate-code`, `$expand`, `$translate`) can be added under `mcp/tools/` using the same pattern.

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
| `MCP_SERVER_NAME` | MCP wrapper display name | `FHIR Terminology MCP Wrapper` |
| `MCP_TRANSPORT` | Wrapper transport (`stdio` or `http`) | `stdio` |
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
