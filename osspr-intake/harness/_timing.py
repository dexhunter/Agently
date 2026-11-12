"""Shared timing helper for intake baselines. Does not import or patch library code."""

from __future__ import annotations

import gc
import json
import statistics
import time
from typing import Any, Callable


def measure(fn: Callable[[], Any], *, repeats: int = 7) -> dict[str, Any]:
    """Warm up once, then time ``repeats`` calls. Noise is the relative range."""

    fn()
    samples_ms: list[float] = []
    for _ in range(repeats):
        gc.collect()
        started = time.perf_counter()
        fn()
        samples_ms.append((time.perf_counter() - started) * 1000.0)
    median_ms = statistics.median(samples_ms)
    noise_pct = 0.0 if median_ms == 0 else (max(samples_ms) - min(samples_ms)) / median_ms * 100.0
    return {
        "repeats": repeats,
        "samples_ms": [round(sample, 4) for sample in samples_ms],
        "median_ms": round(median_ms, 4),
        "noise_pct": round(noise_pct, 4),
    }


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True))
