import json
from pathlib import Path


def save_json_data(data, filename, filepath):
    full_path = Path(filepath) / filename

    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def load_json_data(filepath):
    json_path = Path(filepath)
    with open(json_path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Could not parse JSON file: {json_path}") from exc
