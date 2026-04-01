from typing import Annotated

from fastmcp.tools import tool

from fhir_terminology_http import fhir_get, is_fhir_error_payload


@tool
async def lookup_code(
    system: Annotated[str, "URI of code system (ex: http://snomed.info/sct, http://loinc.org)"],
    code: Annotated[str, "Code to be consulted"],
) -> dict:
    """Consults information about a code in a FHIR terminology system.

    Performs a $lookup operation on the configured FHIR terminology server,
    returning the display name, definition and properties of the code.
    """
    data = await fhir_get(
        "/CodeSystem/$lookup",
        {"system": system, "code": code},
        error_message=f"Error looking up code '{code}' in system '{system}'",
    )
    if is_fhir_error_payload(data):
        return data

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
