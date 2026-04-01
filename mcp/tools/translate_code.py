from __future__ import annotations

from typing import Annotated, Any

from fastmcp.tools import tool

from fhir_terminology_http import fhir_get, is_fhir_error_payload, parameters_flat_map


def _part_map(parts: list[dict[str, Any]] | None) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if not parts:
        return out
    for p in parts:
        name = p.get("name")
        if not name:
            continue
        for key, val in p.items():
            if key == "name" or key == "part":
                continue
            if key.startswith("value") and val is not None:
                out[name] = val
                break
    return out


def _parse_translate_matches(data: dict[str, Any]) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for param in data.get("parameter", []):
        if param.get("name") != "match":
            continue
        parts = param.get("part")
        if not isinstance(parts, list):
            continue
        flat = _part_map(parts)
        entry: dict[str, Any] = {}
        if "equivalence" in flat:
            entry["equivalence"] = str(flat["equivalence"])
        concept = flat.get("concept")
        if isinstance(concept, dict):
            c: dict[str, Any] = {}
            for k in ("system", "code", "display"):
                if k in concept and concept[k] is not None:
                    c[k] = concept[k]
            if c:
                entry["concept"] = c
        if entry:
            matches.append(entry)
    return matches


@tool
async def translate_code(
    system: Annotated[str, "URI of the source code system"],
    code: Annotated[str, "Source code to translate"],
    concept_map_url: Annotated[str, "Canonical URL of the ConceptMap to use"],
    target_system: Annotated[str | None, "Optional target code system URI to filter mappings"] = None,
) -> dict:
    """Translates a code using a ConceptMap (ConceptMap/$translate).

    Returns a list of `matches` with target concepts when the server finds mappings.
    """
    params: dict = {"system": system, "code": code, "url": concept_map_url, "targetsystem": target_system}
    data = await fhir_get(
        "/ConceptMap/$translate",
        params,
        error_message=f"Error translating code '{code}' with map '{concept_map_url}'",
    )
    if is_fhir_error_payload(data):
        return data

    flat = parameters_flat_map(data)
    out: dict[str, Any] = {
        "system": system,
        "code": code,
        "concept_map_url": concept_map_url,
        "matches": _parse_translate_matches(data),
    }
    if "result" in flat:
        out["result"] = bool(flat["result"])
    if "message" in flat and flat["message"] is not None:
        out["message"] = flat["message"]
    return out
