"""Baseline for AgentlyPromptGenerator.to_output_model.

One wide document-extraction schema: a nested object per clause, each with the
same citations list shape. No network and no model call.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agently import Agently
from agently.core import Prompt

from _timing import emit, measure

_CLAUSES = 96


def _schema() -> dict:
    schema = {"overview": (str, "Document overview.")}
    for index in range(_CLAUSES):
        schema[f"clause_{index:03d}"] = {
            "title": (str, "Clause title."),
            "body": (str, "Clause text."),
            "obligation": (str, "Who must act."),
            "citations": [
                {
                    "source": (str, "Source id."),
                    "quote": (str, "Short quote."),
                }
            ],
        }
    return schema


def main() -> None:
    prompt = Prompt(
        Agently.plugin_manager,
        Agently.settings,
        prompt_dict={
            "input": "Extract the clauses.",
            "output": _schema(),
            "output_format": "json",
        },
    )

    def run() -> str:
        model = prompt.to_output_model()
        if model.__name__ != "AgentlyOutput":
            raise RuntimeError(f"unexpected output model {model.__name__}")
        return model.__name__

    run()
    result = measure(run)
    result.update(
        {
            "function": "AgentlyPromptGenerator.to_output_model",
            "clauses": _CLAUSES,
        }
    )
    emit(result)


if __name__ == "__main__":
    main()
