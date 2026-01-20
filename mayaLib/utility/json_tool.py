"""Helpers for reading and writing JSON data used by Maya utility tools."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

JsonSerializable = Any  # Alias to simplify hints while keeping compatibility.


def save_json_data(
    data: JsonSerializable,
    filename: str,
    filepath: str | Path,
) -> Path:
    """Serialise `data` as JSON and persist it alongside the given `filename`.

    Returns the final path to simplify downstream logging/testing.
    """
    full_path = Path(filepath) / filename

    with full_path.open("w", encoding="utf-8") as f:
        json.dump(data, f)

    return full_path


def load_json_data(filepath: str | Path) -> JsonSerializable:
    """Read JSON content from `filepath`, raising a clear error on failure."""
    json_path = Path(filepath)
    with json_path.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Could not parse JSON file: {json_path}") from exc
