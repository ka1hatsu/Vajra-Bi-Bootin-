import json
from pathlib import Path


def load_distros():
    path = Path(__file__).with_name("distros.json")
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)
