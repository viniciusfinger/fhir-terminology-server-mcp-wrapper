# FHIR Terminology Server MCP Wrapper

<p align="center">
  <img src="https://i.ibb.co/CsTXdVb7/logo.png" alt="Model Context Protocol (MCP) plus HL7 FHIR" width="480" />
</p>

## Overview

This project is an **MCP (Model Context Protocol) wrapper**: it turns standard FHIR **Terminology Services** operations into **tools** that LLMs and AI assistants can call safely and predictably.

It is **not** a terminology server. It does not store code systems or ValueSets. It **forwards** requests to a real FHIR terminology backend (for example the public `tx.fhir.org`, or your own HAPI FHIR, Ontoserver, or vendor TS endpoint) and returns normalized results to the client.

Tools and resources are implemented with [FastMCP](https://github.com/jlowin/fastmcp): Python modules under `mcp/tools/` and `mcp/resources/` are loaded via `FileSystemProvider` from `server.py` (see [Run](#run)).

### Why use it?

- **Familiar interface for AI applications** — Any MCP-compatible host (Claude Desktop, custom agents or other MCP servers) can resolve clinical codes without hard-coding HTTP clients or FHIR URLs in the prompt.
- **Reuse your existing stack** — Point `FHIR_TERMINOLOGY_SERVER_URL` at the same server your EHR or integration layer already uses; no duplicate terminology store.
- **Structured, typed calls** — Tools expose parameters such as `system` and `code` instead of asking the model to craft raw operation URLs.
- **Separation of concerns** — Clinical vocabulary stays on the authoritative TS; this repo only bridges MCP ↔ FHIR.

### What you can do with it

- **Resolve codes to human-readable labels** — SNOMED CT, LOINC, ICD, and others (depending on the backend), via `lookup_code` ([`CodeSystem/$lookup`](https://hl7.org/fhir/codesystem-operation-lookup.html)).
- **Validate codes** — Against a whole code system (`validate_code`, [`CodeSystem/$validate-code`](https://hl7.org/fhir/codesystem-operation-validate-code.html)) or against a specific ValueSet (`validate_code_in_valueset`, [`ValueSet/$validate-code`](https://hl7.org/fhir/valueset-operation-validate-code.html)).
- **Expand ValueSets** — List member concepts with `expand_valueset` ([`ValueSet/$expand`](https://hl7.org/fhir/valueset-operation-expand.html)).
- **Map between code systems** — `translate_code` ([`ConceptMap/$translate`](https://hl7.org/fhir/conceptmap-operation-translate.html)).
- **Hierarchical checks** — `subsumes_codes` ([`CodeSystem/$subsumes`](https://hl7.org/fhir/codesystem-operation-subsumes.html)) for is-a relationships where the server supports them.
- **Swap backends** — Use the public terminology service for demos, or a private endpoint for restricted or local code systems.

## MCP tools (FHIR Terminology Services)

Each tool maps to a **GET** on the configured server's base URL, using the FHIR **operation** named below (R4-style paths). Parameters are the query parameters those operations expect; responses are normalized into small JSON objects for the client.

| Tool | FHIR operation | Purpose |
|------|----------------|---------|
| `lookup_code` | `GET CodeSystem/$lookup` | Returns display text and related metadata for a single `system` + `code`. Does not test ValueSet membership or hierarchy. |
| `validate_code` | `GET CodeSystem/$validate-code` | Returns whether a code is valid in the **code system** (and optional display/version checks). Not the same as membership in a ValueSet. |
| `validate_code_in_valueset` | `GET ValueSet/$validate-code` | Returns whether a `system` + `code` is in the expansion of the ValueSet identified by `valueset_url`. |
| `expand_valueset` | `GET ValueSet/$expand` | Expands a ValueSet by canonical `url`, with optional `filter` and `count` (default cap 50 in the tool). Returns a flat list of `contains` entries. |
| `translate_code` | `GET ConceptMap/$translate` | Uses a known `concept_map_url` to map a source `system` + `code` to target concept(s), with optional `target_system`. |
| `subsumes_codes` | `GET CodeSystem/$subsumes` | Compares two codes in the same `system`; `outcome` reflects equivalence or subsumption (`subsumes`, `subsumed-by`, `not-subsumed`, etc.) when the terminology server supports hierarchies. |

Official operation semantics and parameters: [FHIR Terminology Service](https://hl7.org/fhir/terminology-service.html) (R4).

## MCP resources

Resources are **read-only** data exposed to MCP clients (no call to the remote terminology server). They help pick correct canonical URIs before calling tools.

| URI | Name | Purpose |
|-----|------|---------|
| `fhir://code-systems` | FHIR Common Code Systems | JSON catalog of common code systems: canonical URLs, OIDs, domains, descriptions, and example codes. |
| `fhir://code-systems/by-domain/{domain}` | Code Systems by Domain | Same catalog filtered by domain keyword (e.g. `medications`, `laboratory`). If nothing matches, the JSON includes `available_domains`. |

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
# Linux/macOS
cp .env.example .env

# Windows (cmd)
copy .env.example .env
```

| Variable | Description | Default |
|---|---|---|
| `FHIR_TERMINOLOGY_SERVER_URL` | Base URL of the target FHIR terminology server | `https://tx.fhir.org/r4` |
| `FHIR_HTTP_CACHE_ENABLED` | Enable in-memory LRU+TTL cache for cacheable terminology GETs | `true` |
| `FHIR_HTTP_CACHE_TTL_SECONDS` | Time-to-live for cache entries (seconds) | `300` |
| `FHIR_HTTP_CACHE_MAX_ENTRIES` | Maximum cached responses | `512` |
| `MCP_SERVER_NAME` | MCP wrapper display name | `FHIR Terminology Server MCP Wrapper` |
| `PORT` | Port for HTTP transport | `8000` |
| `MCP_ENV` | Set to `development` to reload `mcp/` modules on change (FileSystemProvider) | `production` |

## Run

```bash
# stdio (default for IDE integration)
python server.py

# FastMCP CLI
fastmcp run server.py:mcp
```

## Test

Tests use [pytest](https://pytest.org/). Configuration is in `pytest.ini` (e.g. `testpaths`, `asyncio` mode). Run from the **repository root** with the virtual environment activated:

```bash
pytest -v
```

`-v` prints each test name and outcome; add `-x` to stop on the first failure, or `-k <substring>` to filter by name.

### Markers

Markers group tests by how they behave. This repo uses:

| Marker | Meaning |
|--------|---------|
| `integration` | Hits a real FHIR terminology server (`FHIR_TERMINOLOGY_SERVER_URL` in `.env`). Needs network. |

Examples:

```bash
# Only integration tests
pytest -v -m integration

# One file
pytest -v test/lookup_test.py
```