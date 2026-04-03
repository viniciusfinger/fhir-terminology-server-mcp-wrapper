from typing import Annotated

from fastmcp.tools import tool

from fhir_terminology_http import fhir_get, parameters_flat_map


@tool
async def validate_code_in_valueset(
    valueset_url: Annotated[str, "Canonical URL of the ValueSet (e.g. 'http://hl7.org/fhir/ValueSet/administrative-gender'). Must be a full URL."],
    system: Annotated[str, "Canonical URI of the code system the code belongs to (e.g. 'http://hl7.org/fhir/administrative-gender')."],
    code: Annotated[str, "The code to check against the ValueSet (e.g. 'male'). Must be non-empty."],
    display: Annotated[str | None, "If provided, the server also checks whether this display text matches."] = None,
) -> dict:
    """Check whether a specific code is a member of a ValueSet.

    Returns: {valueset_url, system, code, result (true/false), display, message}.
    result=true means the code belongs to the ValueSet; result=false means it does not.
    Does NOT validate the code against the entire code system (use validate_code for that).
    Does NOT list all codes in the ValueSet (use expand_valueset for that).

    Example: validate_code_in_valueset(valueset_url="http://hl7.org/fhir/ValueSet/administrative-gender", system="http://hl7.org/fhir/administrative-gender", code="male") → result: true.
    """
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