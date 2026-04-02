from typing import Annotated

from fastmcp.tools import tool

from fhir_terminology_http import fhir_get, is_fhir_error_payload, parameters_flat_map


@tool
async def validate_code(
    system: Annotated[str, "URI of the code system (ex: http://snomed.info/sct)"],
    code: Annotated[str, "Code to validate"],
    display: Annotated[str | None, "Optional display string to validate against the code"] = None,
    version: Annotated[str | None, "Optional code system version"] = None,
) -> dict:
    """Validates that a code exists in a FHIR code system (CodeSystem/$validate-code).

    Returns whether the code is valid and the server-recommended display when available.
    """
    params: dict = {"system": system, "code": code, "display": display, "version": version}
    
    data = await fhir_get(
        "/CodeSystem/$validate-code",
        params,
        error_message=f"Error validating code '{code}' in system '{system}'",
    )

    if is_fhir_error_payload(data):
        return data

    flat = parameters_flat_map(data)
    
    out: dict = {"system": system, "code": code}
    
    if "result" in flat:
        out["result"] = bool(flat["result"])
    if "message" in flat and flat["message"] is not None:
        out["message"] = flat["message"]
    if "display" in flat and flat["display"] is not None:
        out["display"] = flat["display"]
    
    return out
