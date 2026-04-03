from typing import Annotated

from fastmcp.tools import tool

from fhir_terminology_http import fhir_get, parameters_flat_map


@tool
async def validate_code_in_valueset(
    valueset_url: Annotated[str, "Canonical URL of the ValueSet"],
    system: Annotated[str, "URI of the code system for the code to validate"],
    code: Annotated[str, "Code to validate against the ValueSet"],
    display: Annotated[str | None, "Optional display string to validate"] = None,
) -> dict:
    """Validates a code against a specific ValueSet (ValueSet/$validate-code)."""
    params: dict = {"url": valueset_url, "system": system, "code": code, "display": display}

    data = await fhir_get(
        "/ValueSet/$validate-code",
        params,
        error_message=f"Error validating code '{code}' in ValueSet '{valueset_url}'",
    )

    flat = parameters_flat_map(data)

    out: dict = {"valueset_url": valueset_url, "system": system, "code": code}

    if "result" in flat:
        out["result"] = bool(flat["result"])
    if "message" in flat and flat["message"] is not None:
        out["message"] = flat["message"]
    if "display" in flat and flat["display"] is not None:
        out["display"] = flat["display"]

    return out