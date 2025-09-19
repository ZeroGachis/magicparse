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

    @abstractmethod
    def apply(self, value: Any) -> Any:
        pass

    @abstractstaticmethod
    def key() -> str:
        pass

    @classmethod
    def register(cls, transform: "Transform") -> None:
        if not hasattr(cls, "registry"):
            cls.registry = {}

        cls.registry[transform.key()] = transform
