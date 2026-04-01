from typing import Annotated

import httpx
from fastmcp.tools import tool

from config import FHIR_SERVER_URL


@tool
async def lookup_code(
    system: Annotated[str, "URI of code system (ex: http://snomed.info/sct, http://loinc.org)"],
    code: Annotated[str, "Code to be consulted"],
) -> dict:
    """Consults information about a code in a FHIR terminology system.

    Performs a $lookup operation on the configured FHIR terminology server,
    returning the display name, definition and properties of the code.
    """
    params = {"system": system, "code": code}

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{FHIR_SERVER_URL}/CodeSystem/$lookup",
            params=params,
            headers={"Accept": "application/fhir+json"},
        )

    if response.status_code != 200:
        return {
            "error": True,
            "status_code": response.status_code,
            "message": f"Error looking up code '{code}' in system '{system}'",
            "details": response.text[:500],
        }

    data = response.json()
    result = {"system": system, "code": code}

    for param in data.get("parameter", []):
        name = param.get("name")
        if name == "display":
            result["display"] = param.get("valueString")
        elif name == "name":
            result["code_system_name"] = param.get("valueString")
        elif name == "version":
            result["version"] = param.get("valueString")

    return result
