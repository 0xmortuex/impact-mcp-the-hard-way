import json
from shop.models import Item


def total(items: list[Item]) -> int:
    return len(json.dumps(items))
