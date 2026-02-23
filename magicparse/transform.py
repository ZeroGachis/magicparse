from abc import ABC, abstractmethod
from collections.abc import Callable, Collection, Sequence
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Any, NoReturn, Self
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


class TransformError(Exception):
    def __init__(self, message: str, params: Sequence[Any] | dict[str, Any]) -> None:
        super().__init__(message)
        match params:
            case dict():
                for param, value in params.items():
                    self.add_note(f"param({param}) = {value}")
            case _:
                for i, value in enumerate(params):
                    self.add_note(f"param({i}) = {value}")


def coalesce_numbers[T: int | float | Decimal | None](*args: T | None) -> T:
    for arg in args:
        if arg:
            return arg

    raise TransformError("No non-zero value to coalesce into", params=args)


def divide[T: int | Decimal](numerator: T, denominator: T) -> float | Decimal:
    "JSONata native x / y operator can only divide int and float, but not Decimal"
    try:
        return numerator / denominator
    except Exception as error:
        raise TransformError("Cannot divide", params={"numerator": numerator, "denominator": denominator}) from error


def assert_positive[T: int | float | Decimal](value: T) -> T:
    if value <= 0:
        raise TransformError("Value is not positive", params={"value": value})
    return value


def is_zero(value: int | float | Decimal) -> bool:
    return value == 0


def left_pad_zeroes(value: str, width: int) -> str:
    try:
        return value.zfill(width)
    except Exception as error:
        raise TransformError("Cannot left pad zeroes", params={"value": value, "width": width}) from error


def length(value: Collection[Any]) -> int:
    try:
        return len(value)
    except Exception as error:
        raise TransformError("Cannot get length", params={"value": value}) from error


def map_to[K, V](key: K, mapping: dict[K, V]) -> V:
    try:
        return mapping[key]
    except Exception as error:
        raise TransformError("Cannot map to", params={"key": key, "mapping": mapping}) from error


class SkippedRow(Exception):
    pass


def skip_row(reason: str | None) -> NoReturn:
    raise SkippedRow(reason or "")


def skip_row_if(condition: bool, reason: str | None) -> None:
    if condition:
        raise SkippedRow(reason or "")


def strip_whitespaces(value: str) -> str:
    try:
        return value.strip()
    except Exception as error:
        raise TransformError("Cannot strip whitespaces", params={"value": value}) from error


def to_decimal(value: str | float | int) -> Decimal:
    try:
        if isinstance(value, str):
            return Decimal(value.strip().replace(",", "."))
        else:
            return Decimal(value)
    except Exception as error:
        raise TransformError("Cannot convert to decimal", params={"value": value}) from error


def to_int(value: str) -> int:
    try:
        return int(value.strip())
    except Exception as error:
        raise TransformError("Cannot convert to int", params={"value": value}) from error


def type_of(value: Any) -> str:
    match value:
        case int():
            return "int"
        case float():
            return "float"
        case Decimal():
            return "decimal"
        case str():
            return "string"
        case _:
            return str(type(value))  # pyright: ignore[reportUnknownArgumentType]


class Transform(Jsonata):
    def __init__(self, expression: str) -> None:
        super().__init__(expression)
        self.validate_input = False

    @staticmethod
    def get_builtin_functions() -> dict[str, Callable[..., Any]]:
        return {
            "assert_positive": assert_positive,
            "coalesce_numbers": coalesce_numbers,
            "divide": divide,
            "is_zero": is_zero,
            "left_pad_zeroes": left_pad_zeroes,
            "length": length,
            "map_to": map_to,
            "skip_row": skip_row,
            "skip_row_if": skip_row_if,
            "strip_whitespaces": strip_whitespaces,
            "to_decimal": to_decimal,
            "to_int": to_int,
            "type_of": type_of,
        }


def _register_builtin_functions():
    for function_name, function in Transform.get_builtin_functions().items():
        Jsonata.static_frame.bind(function_name, Jsonata.JLambda(function))


_register_builtin_functions()
