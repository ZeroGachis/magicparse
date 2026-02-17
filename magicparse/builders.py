from abc import ABC
from decimal import Decimal
from typing import Any, cast

from .transform import ParsingTransform, OnError


class Builder(ParsingTransform, ABC):
    registry = dict[str, type["Builder"]]()

    @classmethod
    def build(cls, options: dict[str, Any]) -> "Builder":
        try:
            name = options["name"]
        except:
            raise ValueError("builder must have a 'name' key")

        try:
            builder = cls.registry[name]
        except:
            raise ValueError(f"invalid builder '{name}'")

        on_error = options.get("on-error", OnError.RAISE)
        if "parameters" in options:
            return builder(on_error=on_error, **options["parameters"])
        else:
            return builder(on_error=on_error)


class Concat(Builder):
    def __init__(self, on_error: OnError, fields: Any) -> None:
        super().__init__(on_error)
        if (
            not isinstance(fields, list)
            or not all(isinstance(field, str) for field in fields)  # type: ignore[reportUnknownVariableType]
            or len(fields) < 2  # type: ignore[reportUnknownVariableType]
        ):
            raise ValueError(
                "composite-processor 'concat': 'fields' parameter must be a list[str] with at least two elements"
            )
        self.fields = cast(list[str], fields)

    def apply(self, value: dict[str, Any]) -> str:
        return "".join(value[field] for field in self.fields)

    @staticmethod
    def key() -> str:
        return "concat"


class Divide(Builder):
    def __init__(self, on_error: OnError, numerator: Any, denominator: Any) -> None:
        super().__init__(on_error)
        if not numerator or not isinstance(numerator, str):
            raise ValueError("builder 'divide': 'numerator' parameter must be a non null str")
        if not denominator or not isinstance(denominator, str):
            raise ValueError("builder 'divide': 'denominator' parameter must be a non null str")
        self.numerator = numerator
        self.denominator = denominator

    def apply(self, value: dict[str, Any]) -> Decimal:
        return value[self.numerator] / value[self.denominator]

    @staticmethod
    def key() -> str:
        return "divide"


class Multiply(Builder):
    def __init__(self, on_error: OnError, x_factor: Any, y_factor: Any) -> None:
        super().__init__(on_error)
        if not x_factor or not isinstance(x_factor, str):
            raise ValueError("builder 'multiply': 'x_factor' parameter must be a non null str")
        if not y_factor or not isinstance(y_factor, str):
            raise ValueError("builder 'multiply': 'y_factor' parameter must be a non null str")
        self.x_factor = x_factor
        self.y_factor = y_factor

    def apply(self, value: dict[str, Any]):
        return value[self.x_factor] * value[self.y_factor]

    @staticmethod
    def key() -> str:
        return "multiply"


class Coalesce(Builder):
    def __init__(self, on_error: OnError, fields: Any) -> None:
        super().__init__(on_error)
        if not fields:
            raise ValueError("parameters should defined fields to coalesce")
        if not isinstance(fields, list) or not all(isinstance(field, str) for field in fields) or len(fields) < 2:  # type: ignore[reportUnknownVariableType]
            raise ValueError("parameters should have two fields at least")

        self.fields = cast(list[str], fields)

    def apply(self, value: dict[str, Any]) -> str | None:
        for field in self.fields:
            if value[field]:
                return value[field]
        return None

    @staticmethod
    def key() -> str:
        return "coalesce"


builtins = [Concat, Divide, Multiply, Coalesce]
