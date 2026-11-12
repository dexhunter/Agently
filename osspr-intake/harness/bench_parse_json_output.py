"""Baseline for StructuredOutputParser.parse_json_output.

A fenced-style model reply whose body is strict JSON. No network.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agently.core.model.StructuredOutputParser import parse_json_output

from _timing import emit, measure


def _document() -> tuple[str, dict]:
    payload = {
        "summary": "Structured findings from the repository pass.",
        "items": [
            {
                "id": f"item-{index}",
                "title": f"Finding {index}",
                "body": "Observed behavior in the worker path. " * 8,
                "score": round((index % 10) / 10, 1),
                "tags": ["runtime", "parser"],
                "ok": True,
            }
            for index in range(24)
        ],
    }
    text = "Structured result follows.\n" + json.dumps(payload)
    schema = {
        "summary": (str, "summary"),
        "items": [{"id": (str, "id"), "body": (str, "body")}],
    }
    return text, schema


def main() -> None:
    text, schema = _document()

    def run() -> int:
        _cleaned, parsed, _model, repaired = parse_json_output(text, schema, lambda value: None)
        if repaired or not isinstance(parsed, dict):
            raise RuntimeError("expected a strict JSON object parse")
        return len(parsed["items"])

    if run() != 24:
        raise RuntimeError("parse_json_output did not return 24 items")
    result = measure(run)
    result.update(
        {
            "function": "parse_json_output",
            "input_chars": len(text),
            "items": 24,
        }
    )
    emit(result)


if __name__ == "__main__":
    main()
