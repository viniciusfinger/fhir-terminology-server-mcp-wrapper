import os
import logging

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fhir-terminology-server-mcp-wrapper")

FHIR_SERVER_URL = os.getenv("FHIR_TERMINOLOGY_SERVER_URL", "https://tx.fhir.org/r4")
SERVER_NAME = os.getenv("MCP_SERVER_NAME", "FHIR Terminology Server MCP Wrapper")
