from __future__ import annotations

import asyncio
from typing import Any

import httpx

from config import FHIR_SERVER_URL

FHIR_JSON_ACCEPT = "application/fhir+json"
HTTP_TIMEOUT = 30.0
ERROR_DETAILS_MAX_LEN = 500

_client: httpx.AsyncClient | None = None
_client_loop: asyncio.AbstractEventLoop | None = None


def _get_client() -> httpx.AsyncClient:
    global _client, _client_loop
    loop = asyncio.get_running_loop()
    if _client is None or _client.is_closed or _client_loop is not loop:
        _client = httpx.AsyncClient(
            base_url=FHIR_SERVER_URL.rstrip("/"),
            headers={"Accept": FHIR_JSON_ACCEPT},
            timeout=HTTP_TIMEOUT,
        )
        _client_loop = loop
    return _client


def _clean_params(params: dict[str, str | int | bool | None]) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in params.items():
        if v is None:
            continue
        if isinstance(v, bool):
            out[k] = "true" if v else "false"
        else:
            out[k] = str(v)
    return out


async def fhir_get(
    path: str,
    params: dict[str, str | int | bool | None],
    *,
    error_message: str,
) -> dict[str, Any]:
    """GET {base_url}{path} with FHIR JSON Accept header.

    On non-200, returns {error, status_code, message, details}.
    On success, returns the parsed JSON object (dict).
    """
    if not path.startswith("/"):
        path = "/" + path
    query = _clean_params(params)

    client = _get_client()
    response = await client.get(path, params=query)

    if response.status_code != 200:
        return {
            "error": True,
            "status_code": response.status_code,
            "message": error_message,
            "details": response.text[:ERROR_DETAILS_MAX_LEN],
        }

    return response.json()


def parameters_flat_map(data: dict[str, Any]) -> dict[str, Any]:
    """Map top-level Parameters.parameter[] by name to primitive values.

    For each parameter, picks the first present value* key (valueBoolean,
    valueString, valueCode, etc.). Nested part[] is not flattened here.
    """
    out: dict[str, Any] = {}
    for param in data.get("parameter", []):
        name = param.get("name")

        if not name:
            continue

        for key, val in param.items():
            if key == "name" or key == "part":
                continue

            if key.startswith("value") and val is not None:
                out[name] = val
                break
    
    return out


def is_fhir_error_payload(payload: dict[str, Any]) -> bool:
    return payload.get("error") is True
