"""Integration tests: MCP `validate_code` against `validate_code_ground_truth.json`."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from fastmcp import Client

from server import mcp

GROUND_TRUTH_PATH = Path(__file__).resolve().parent / "ground_truth" / "validate_code_ground_truth.json"


def _load_cases() -> list[dict[str, Any]]:
    with GROUND_TRUTH_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "cases" in data:
        return data["cases"]
    raise ValueError("Ground truth must be a list or an object with a 'cases' array.")


def _case_id(case: dict[str, Any]) -> str:
    cid = case.get("id")
    if cid:
        return str(cid)
    inp = case.get("input") or {}
    return f"{inp.get('system', '')}|{inp.get('code', '')!r}"


def _assert_matches_expected(actual: dict[str, Any], expected: dict[str, Any]) -> None:
    for key, exp_val in expected.items():
        if key in ("error", "status_code"):
            continue
        got = actual.get(key)
        assert got == exp_val, f"key {key!r}: expected {exp_val!r}, got {got!r}"


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.parametrize("case", _load_cases(), ids=_case_id)
async def test_validate_code_matches_ground_truth(case: dict[str, Any]) -> None:
    expected = case["expected_output"]
    inp = case["input"]

    async with Client(mcp) as client:
        result = await client.call_tool("validate_code", inp, raise_on_error=False)

    if expected.get("error") is True:
        assert result.is_error, f"expected isError=True, got {result!r}"
        error_text = result.content[0].text if result.content else ""
        if "status_code" in expected:
            assert str(expected["status_code"]) in error_text, (
                f"expected HTTP {expected['status_code']} in error: {error_text}"
            )
        return

    assert not result.is_error, f"unexpected error: {result!r}"
    actual = result.data if result.data is not None else result.structured_content
    assert actual is not None and isinstance(actual, dict), f"unexpected result: {result!r}"

    _assert_matches_expected(actual, expected)
