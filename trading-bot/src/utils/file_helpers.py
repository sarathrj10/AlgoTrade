import json
import os

def load_state(path):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_state(state, path):
    with open(path, "w") as f:
        json.dump(state, f, indent=2)
