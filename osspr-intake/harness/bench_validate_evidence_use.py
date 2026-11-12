"""Baseline for EvidenceLedger.validate_evidence_use.

One guard pass over composite file references. Exact alias lookup misses, so
each claim scans ledger anchors. No network.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agently.builtins.plugins.AgentExecution.long_task.EvidenceLedger import (
    EVIDENCE_LEDGER_VIEW_SCHEMA_VERSION,
    validate_evidence_use,
)

from _timing import emit, measure

_ITEMS = 160
_CLAIMS = 40


def _inputs() -> tuple[list[dict], dict]:
    items = [
        {
            "id": f"ev-{index}",
            "kind": "source",
            "status": "ok",
            "body_state": "full",
            "cite_as": f"e{index + 1}",
            "reference_id": f"ref-{index}",
            "path": f"docs/guide/section_{index}.md",
            "title": f"Section {index} streaming parser notes",
            "heading": f"Heading {index}",
            "aliases": [f"section-{index}", f"guide-{index}"],
        }
        for index in range(_ITEMS)
    ]
    # Path plus heading is the composite shape the anchor resolver documents.
    # It does not equal a precomputed alias, so validation takes the scan path.
    evidence_use = [
        {
            "claim": f"Section {index} describes the worker path.",
            "support_type": "content",
            "evidence_ids": [f"docs/guide/section_{index}.md heading {index}"],
        }
        for index in range(0, _ITEMS, _ITEMS // _CLAIMS)
    ]
    ledger = {
        "schema_version": EVIDENCE_LEDGER_VIEW_SCHEMA_VERSION,
        "items": items,
    }
    return evidence_use, ledger


def main() -> None:
    evidence_use, ledger = _inputs()

    def run() -> int:
        guard = validate_evidence_use(evidence_use, ledger)
        if not guard.get("valid"):
            raise RuntimeError(f"evidence guard failed: {guard.get('diagnostics')[:2]}")
        if guard.get("checked_claims") != len(evidence_use):
            raise RuntimeError("evidence guard did not check every claim")
        anchor_hits = sum(
            1
            for item in guard.get("diagnostics") or []
            if item.get("basis") == "anchor"
        )
        if anchor_hits != len(evidence_use):
            raise RuntimeError(f"expected every claim to resolve by anchor, got {anchor_hits}")
        return anchor_hits

    claims = run()
    result = measure(run)
    result.update(
        {
            "function": "validate_evidence_use",
            "ledger_items": _ITEMS,
            "claims": claims,
        }
    )
    emit(result)


if __name__ == "__main__":
    main()
