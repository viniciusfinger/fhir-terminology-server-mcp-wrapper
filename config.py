import os
import logging

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fhir-terminology-server-mcp-wrapper")

FHIR_SERVER_URL = os.getenv("FHIR_TERMINOLOGY_SERVER_URL", "https://tx.fhir.org/r4")
SERVER_NAME = os.getenv("MCP_SERVER_NAME", "FHIR Terminology Server MCP Wrapper")

FHIR_HTTP_CACHE_ENABLED = os.getenv("FHIR_HTTP_CACHE_ENABLED", "true").lower() in (
    "1",
    "true",
    "yes",
)

FHIR_HTTP_CACHE_TTL_SECONDS = max(
    1.0,
    float(os.getenv("FHIR_HTTP_CACHE_TTL_SECONDS", "300")),
)

FHIR_HTTP_CACHE_MAX_ENTRIES = max(
    1,
    int(os.getenv("FHIR_HTTP_CACHE_MAX_ENTRIES", "512")),
)
