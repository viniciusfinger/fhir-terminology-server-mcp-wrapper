from typing import Annotated

from fastmcp.tools import tool

from fhir_terminology_http import fhir_get


@tool
async def lookup_code(
    system: Annotated[str, "Canonical URI of the code system (e.g. 'http://snomed.info/sct', 'http://loinc.org'). Must be a full URI, not an abbreviation like 'SNOMED'."],
    code: Annotated[str, "The code to look up (e.g. '73211009', '718-7'). Must be non-empty."],
) -> dict:
    """Look up the display name and metadata for a single code in a FHIR code system.

    Returns: {system, code, display, code_system_name, version}.
    Use when you need to find what a code means or get its human-readable display name.
    Does NOT validate membership in a ValueSet (use validate_code_in_valueset).
    Does NOT check parent/child hierarchy (use subsumes_codes).
    Only supports one code per call.

    Example: lookup_code(system="http://snomed.info/sct", code="73211009") → display: "Diabetes mellitus".
    """
    data = await fhir_get(
        "/CodeSystem/$lookup",
        {"system": system, "code": code},
        error_message=f"Error looking up code '{code}' in system '{system}'",
    )

    result: dict = {"system": system, "code": code}

    for param in data.get("parameter", []):
        name = param.get("name")
        if name == "display":
            result["display"] = param.get("valueString")
        elif name == "name":
            result["code_system_name"] = param.get("valueString")
        elif name == "version":
            result["version"] = param.get("valueString")

    return result
