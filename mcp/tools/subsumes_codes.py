from typing import Annotated

from fastmcp.tools import tool

from fhir_terminology_http import fhir_get, parameters_flat_map


@tool
async def subsumes_codes(
    system: Annotated[str, "Canonical URI of the code system (e.g. 'http://snomed.info/sct'). Both codes must belong to this system."],
    code_a: Annotated[str, "First code to compare (e.g. '404684003' for Clinical finding)."],
    code_b: Annotated[str, "Second code to compare (e.g. '73211009' for Diabetes mellitus)."],
) -> dict:
    """Test the hierarchical (is-a) relationship between two codes in the same code system.

    Returns: {system, code_a, code_b, outcome}.
    outcome is one of: "equivalent" (same concept), "subsumes" (code_a is a parent of code_b),
    "subsumed-by" (code_a is a child of code_b), or "not-subsumed" (no hierarchical relationship).
    Both codes must belong to the same code system — cannot compare across systems.
    Does NOT look up code details (use lookup_code for that).
    Only works with code systems that have a hierarchy (e.g. SNOMED CT, ICD-10).

    Example: subsumes_codes(system="http://snomed.info/sct", code_a="404684003", code_b="73211009") → outcome: "subsumes" (Clinical finding subsumes Diabetes mellitus).
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
