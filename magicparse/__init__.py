from .schema import Schema
from typing import Any, Dict, List, Tuple


__all__ = ["parse", "Schema"]


def parse(data: str, schema_options: Dict[str, Any]) -> Tuple[List[dict], List[dict]]:
    schema = Schema.build(schema_options)
    return schema.parse(data)
