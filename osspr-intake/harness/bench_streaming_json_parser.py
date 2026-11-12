"""Baseline for StreamingJSONParser.parse_stream.

Token-sized chunks of one strict JSON object that stays under the default
1024-character incremental-parse cap. No network.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agently.utils.StreamingJSONParser import StreamingJSONParser

from _timing import emit, measure

_SCHEMA = {
    "reply": (str, "reply"),
    "confidence": (float, "confidence"),
    "notes": [(str, "note")],
    "items": [{"id": (int, "id"), "text": (str, "text")}],
}


def _pieces() -> tuple[str, list[str]]:
    payload = {
        "reply": "Use the cited notes and keep the declared structure.",
        "confidence": 0.82,
        "notes": [
            "The parser repairs trailing commas before validation.",
            "Prompt titles stay stable across turns.",
            "Evidence ids are resolved before the final answer.",
        ],
        "items": [
            {"id": index, "text": f"finding {index} stays within the contract"}
            for index in range(6)
        ],
    }
    raw = json.dumps(payload)
    if len(raw) > 1024:
        raise RuntimeError(f"payload exceeds the default incremental cap: {len(raw)}")
    pieces = [raw[index : index + 24] for index in range(0, len(raw), 24)]
    return raw, pieces


async def _parse(pieces: list[str]) -> int:
    parser = StreamingJSONParser(_SCHEMA)

    async def chunks():
        for piece in pieces:
            yield piece

    events = 0
    async for _event in parser.parse_stream(chunks()):
        events += 1
    items = parser.current_data.get("items") if isinstance(parser.current_data, dict) else None
    if not isinstance(items, list) or len(items) != 6 or events <= 0:
        raise RuntimeError("streaming parse did not recover the six items")
    return events


def main() -> None:
    raw, pieces = _pieces()
    loop = asyncio.new_event_loop()
    try:
        def run() -> int:
            return loop.run_until_complete(_parse(pieces))

        run()
        result = measure(run)
    finally:
        loop.close()
    result.update(
        {
            "function": "StreamingJSONParser.parse_stream",
            "input_chars": len(raw),
            "chunks": len(pieces),
            "chunk_chars": 24,
            "max_incomplete_parse_chars": StreamingJSONParser.DEFAULT_MAX_INCOMPLETE_PARSE_CHARS,
        }
    )
    emit(result)


if __name__ == "__main__":
    main()
