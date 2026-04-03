from typing import Annotated

from fastmcp.tools import tool

from fhir_terminology_http import fhir_get, parameters_flat_map


@tool
async def subsumes_codes(
    system: Annotated[str, "URI of the code system (ex: http://snomed.info/sct)"],
    code_a: Annotated[str, "First code (codeA in FHIR $subsumes)"],
    code_b: Annotated[str, "Second code (codeB in FHIR $subsumes)"],
) -> dict:
    """Tests subsumption between two codes in the same code system (CodeSystem/$subsumes).

    Outcome values include equivalent, subsumes, subsumed-by, not-subsumed, etc.
    """
    data = await fhir_get(
        "/CodeSystem/$subsumes",
        {"system": system, "codeA": code_a, "codeB": code_b},
        error_message=f"Error testing subsumption for '{code_a}' and '{code_b}' in '{system}'",
    )

    flat = parameters_flat_map(data)
    out: dict = {"system": system, "code_a": code_a, "code_b": code_b}
    if "outcome" in flat and flat["outcome"] is not None:
        out["outcome"] = str(flat["outcome"])
    return out
