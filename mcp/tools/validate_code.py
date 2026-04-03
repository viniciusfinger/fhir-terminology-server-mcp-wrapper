from typing import Annotated

from fastmcp.tools import tool

from fhir_terminology_http import fhir_get, parameters_flat_map


@tool
async def validate_code(
    system: Annotated[str, "Canonical URI of the code system (e.g. 'http://snomed.info/sct'). Must be a full URI, not an abbreviation."],
    code: Annotated[str, "The code to validate (e.g. '73211009'). Must be non-empty."],
    display: Annotated[str | None, "If provided, the server also checks whether this display text matches the code."] = None,
    version: Annotated[str | None, "Specific code system version to validate against. Omit to use the server default."] = None,
) -> dict:
    """Check whether a code exists and is valid within a code system.

    Returns: {system, code, result (true/false), display, message}.
    result=true means the code is recognized; result=false means it is not found or inactive.
    Does NOT check membership in a ValueSet (use validate_code_in_valueset for that).
    Does NOT return code properties or definitions (use lookup_code for that).

    Example: validate_code(system="http://loinc.org", code="718-7") → result: true, display: "Hemoglobin [Mass/volume] in Blood".
    """
    params: dict = {"system": system, "code": code, "display": display, "version": version}

    data = await fhir_get(
        "/CodeSystem/$validate-code",
        params,
        error_message=f"Error validating code '{code}' in system '{system}'",
    )

    flat = parameters_flat_map(data)

    out: dict = {"system": system, "code": code}

    if "result" in flat:
        out["result"] = bool(flat["result"])
    if "message" in flat and flat["message"] is not None:
        out["message"] = flat["message"]
    if "display" in flat and flat["display"] is not None:
        out["display"] = flat["display"]

    return out
