from typing import Any


def setattribute(value: dict | object, k: str, v: Any):
    if hasattr(value, "__setattr__"):
        value.__setattr__(k, v)
    return value
