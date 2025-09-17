from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class LastTransformSuccess:
    value: Any


@dataclass(frozen=True, slots=True)
class LastTransformFailed:
    skip_row: bool = False
