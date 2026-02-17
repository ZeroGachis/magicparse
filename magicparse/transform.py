from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Self
from jsonata import Jsonata  # pyright: ignore[reportMissingTypeStubs]


@dataclass(frozen=True, slots=True)
class Ok:
    value: Any


@dataclass(frozen=True, slots=True)
class SkipRow:
    exception: Exception


type Result = Ok | SkipRow


class OnError(StrEnum):
    RAISE = "raise"
    SKIP_ROW = "skip-row"


class ParsingTransform(ABC):
    registry: dict[str, type[Self]]

    def __init__(self, on_error: OnError) -> None:
        self.on_error = on_error

    @classmethod
    @abstractmethod
    def build(cls, options: dict[str, Any]) -> "ParsingTransform":
        pass

    @abstractmethod
    def apply(self, value: Any) -> Any:
        pass

    @staticmethod
    @abstractmethod
    def key() -> str:
        pass

    @classmethod
    def register(cls, transform: type[Self]) -> None:
        cls.registry[transform.key()] = transform


class Transform(Jsonata):
    @classmethod
    def build(cls, expression: str) -> "Transform":
        return Transform(expr=expression)
