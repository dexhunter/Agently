"""Baseline for StructuredOutputParser.parse_yaml_literal_output.

Fenced YAML document of the same shape as a yaml_literal model reply. No network.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agently.core.model.StructuredOutputParser import parse_yaml_literal_output

from _timing import emit, measure


def _document() -> str:
    payload = {
        "summary": "Structured findings from the repository pass.",
        "items": [
            {
                "id": f"item-{index}",
                "title": f"Finding {index}",
                "body": "Observed behavior in the worker path. " * 6,
                "score": round((index % 10) / 10, 1),
                "tags": ["runtime", "parser"],
                "ok": True,
            }
            for index in range(180)
        ],
    }
    body = yaml.safe_dump(payload, allow_unicode=True, sort_keys=True)
    return "```yaml\n" + body + "```"


def main() -> None:
    document = _document()
    schema = {"summary": (str, "summary"), "items": [{"id": (str, "id")}]}

    def run() -> int:
        parsed = parse_yaml_literal_output(document, schema)
        if not isinstance(parsed, dict) or len(parsed.get("items", [])) != 180:
            raise RuntimeError("yaml literal parse did not return 180 items")
        return len(parsed["items"])

    run()
    result = measure(run)
    result.update(
        {
            "function": "parse_yaml_literal_output",
            "input_chars": len(document),
            "items": 180,
            "c_safe_loader_available": hasattr(yaml, "CSafeLoader"),
        }
    )
    emit(result)


if __name__ == "__main__":
    main()
