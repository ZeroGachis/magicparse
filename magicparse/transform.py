from abc import ABC, abstractclassmethod, abstractmethod, abstractstaticmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


@dataclass(frozen=True, slots=True)
class Ok:
    value: Any


@dataclass(frozen=True, slots=True)
class SkipRow:
    exception: Exception


type Result = Ok | SkipRow


class OnError(Enum):
    RAISE = "raise"
    SKIP_ROW = "skip-row"


class Transform(ABC):
    def __init__(self, on_error: OnError) -> None:
        self.on_error = on_error

    @abstractclassmethod
    def build(cls, options: dict) -> "Transform":
        pass

    def apply(self, last_result: Result) -> Result:
        if isinstance(last_result, SkipRow):
            return last_result

        try:
            return Ok(value=self.transform(last_result.value))
        except Exception as exc:
            if self.on_error == OnError.SKIP_ROW.value:
                return SkipRow(exception=exc)
            raise

    @abstractmethod
    def transform(self, value: Any | None) -> Any | None:
        pass

    @abstractstaticmethod
    def key() -> str:
        pass

    @classmethod
    def register(cls, transform: "Transform") -> None:
        if not hasattr(cls, "registry"):
            cls.registry = {}

        cls.registry[transform.key()] = transform
