import json
from pathlib import Path


def save_json_data(data, filename, filepath):
    full_path = Path(filepath) / filename

    with open(full_path, 'w') as f:
        json.dump(data, f)

def load_json_data(filepath):
    f = open(filepath)
    data = json.load(f)
    f.close()

    return data