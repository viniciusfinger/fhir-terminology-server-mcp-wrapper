"""Integration tests: MCP `expand_valueset` against `expand_valueset_ground_truth.json`."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from fastmcp import Client

from server import mcp

GROUND_TRUTH_PATH = Path(__file__).resolve().parent / "ground_truth" / "expand_valueset_ground_truth.json"


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
    return f"{inp.get('url', '')}"


def _assert_matches_expected(actual: dict[str, Any], expected: dict[str, Any]) -> None:
    for key, exp_val in expected.items():
        if key == "error" and exp_val is False:
            assert actual.get("error") is not True, (
                f"expected success (no error), got {actual!r}"
            )
        else:
            got = actual.get(key)
            assert got == exp_val, f"key {key!r}: expected {exp_val!r}, got {got!r}"


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.parametrize("case", _load_cases(), ids=_case_id)
async def test_expand_valueset_matches_ground_truth(case: dict[str, Any]) -> None:
    expected = case["expected_output"]
    inp = case["input"]

    async with Client(mcp) as client:
        result = await client.call_tool("expand_valueset", inp)

    actual = result.data if result.data is not None else result.structured_content
    assert actual is not None and isinstance(actual, dict), f"unexpected result: {result!r}"

    _assert_matches_expected(actual, expected)

    if expected.get("error") is not True:
        assert "contains" in actual, f"success response must have 'contains': {actual!r}"
        assert isinstance(actual["contains"], list), f"'contains' must be a list: {actual!r}"

        count_limit = inp.get("count")
        if count_limit is not None:
            assert len(actual["contains"]) <= count_limit, (
                f"contains length {len(actual['contains'])} exceeds requested count {count_limit}"
            )
