import json
from typing import Any


def encoder(data: Any):
    return json.loads(json.dumps(data, default=str))
