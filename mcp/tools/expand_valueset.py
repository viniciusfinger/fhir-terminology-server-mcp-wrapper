from typing import Annotated, Any

from fastmcp.tools import tool

from fhir_terminology_http import fhir_get, is_fhir_error_payload


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
    url: Annotated[str, "Canonical URL of the ValueSet to expand"],
    filter: Annotated[str | None, "Text filter applied during expansion (server-dependent)"] = None,
    count: Annotated[int | None, "Maximum number of concepts to return (default 50)"] = None,
) -> dict:
    """Expands a ValueSet against the terminology server (ValueSet/$expand).

    Returns a simplified list of codes under `contains` suitable for LLM consumption.
    """
    effective_count = 50 if count is None else count
    params: dict = {"url": url, "filter": filter, "count": effective_count}
    data = await fhir_get(
        "/ValueSet/$expand",
        params,
        error_message=f"Error expanding ValueSet '{url}'",
    )
    if is_fhir_error_payload(data):
        return data

    expansion = data.get("expansion") or {}
    raw = expansion.get("contains") or []
    contains = [_contains_entry(x) for x in raw if isinstance(x, dict)]

    out: dict = {"url": url, "contains": contains}
    if "total" in expansion and expansion["total"] is not None:
        out["total"] = expansion["total"]
    return out
