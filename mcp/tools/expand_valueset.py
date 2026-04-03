from typing import Annotated, Any

from fastmcp.tools import tool

from fhir_terminology_http import fhir_get


def _contains_entry(item: dict[str, Any]) -> dict[str, Any]:
    row: dict[str, Any] = {}
    if "system" in item:
        row["system"] = item["system"]
    if "code" in item:
        row["code"] = item["code"]
    if "display" in item:
        row["display"] = item["display"]
    return row


@tool
async def expand_valueset(
    url: Annotated[str, "Canonical URL of the ValueSet to expand (e.g. 'http://hl7.org/fhir/ValueSet/administrative-gender'). Must be a full URL."],
    filter: Annotated[str | None, "Free-text search to narrow results (e.g. 'diab' to find diabetes-related codes). Behavior is server-dependent."] = None,
    count: Annotated[int | None, "Maximum number of codes to return. Defaults to 50 if omitted. Use a small value when you only need a few examples."] = None,
) -> dict:
    """List all codes contained in a ValueSet by expanding it.

    Returns: {url, contains: [{system, code, display}], total}.
    contains is a flat list of concepts; total is the full count when provided by the server.
    Defaults to returning at most 50 codes — set count to increase or decrease.
    Does NOT validate a specific code (use validate_code_in_valueset for that).
    Does NOT search for ValueSets by name — you must provide the exact canonical URL.

    Example: expand_valueset(url="http://hl7.org/fhir/ValueSet/administrative-gender") → contains: [{code: "male", display: "Male"}, {code: "female", display: "Female"}, ...].
    """
    effective_count = 50 if count is None else count
    params: dict = {"url": url, "filter": filter, "count": effective_count}
    data = await fhir_get(
        "/ValueSet/$expand",
        params,
        error_message=f"Error expanding ValueSet '{url}'",
    )

    expansion = data.get("expansion") or {}
    raw = expansion.get("contains") or []
    contains = [_contains_entry(x) for x in raw if isinstance(x, dict)]

    out: dict = {"url": url, "contains": contains}
    if "total" in expansion and expansion["total"] is not None:
        out["total"] = expansion["total"]
    return out
