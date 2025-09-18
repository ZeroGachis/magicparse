from abc import ABC
from decimal import Decimal

from .transform import Transform


class Builder(Transform, ABC):
    @classmethod
    def build(cls, options: dict) -> "Builder":
        try:
            name = options["name"]
        except:
            raise ValueError("builder must have a 'name' key")

        try:
            builder = cls.registry[name]
        except:
            raise ValueError(f"invalid builder '{name}'")

        on_error = options.get("on-error", "raise")
        if "parameters" in options:
            return builder(on_error=on_error, **options["parameters"])
        else:
            return builder(on_error=on_error)


class Concat(Builder):
    def __init__(self, on_error: str, fields: list[str]) -> None:
        super().__init__(on_error)
        if (
            not fields
            or isinstance(fields, str)
            or not isinstance(fields, list)
            or not all(isinstance(field, str) for field in fields)
            or len(fields) < 2
        ):
            raise ValueError(
                "composite-processor 'concat': "
                "'fields' parameter must be a list[str] with at least two elements"
            )

        self.fields = fields

    def transform(self, row: dict) -> str:
        return "".join(row[field] for field in self.fields)

    @staticmethod
    def key() -> str:
        return "concat"


class Divide(Builder):
    def __init__(self, on_error: str, numerator: str, denominator: str) -> None:
        super().__init__(on_error)
        if not numerator or not isinstance(numerator, str):
            raise ValueError(
                "builder 'divide': " "'numerator' parameter must be a non null str"
            )
        if not denominator or not isinstance(denominator, str):
            raise ValueError(
                "builder 'divide': " "'denominator' parameter must be a non null str"
            )
        self.numerator = numerator
        self.denominator = denominator

    def transform(self, row: dict) -> Decimal:
        return row[self.numerator] / row[self.denominator]

    @staticmethod
    def key() -> str:
        return "divide"


class Multiply(Builder):
    def __init__(self, on_error: str, x_factor: str, y_factor: str) -> None:
        super().__init__(on_error)
        if not x_factor or not isinstance(x_factor, str):
            raise ValueError(
                "builder 'multiply': " "'x_factor' parameter must be a non null str"
            )
        if not y_factor or not isinstance(y_factor, str):
            raise ValueError(
                "builder 'multiply': " "'y_factor' parameter must be a non null str"
            )
        self.x_factor = x_factor
        self.y_factor = y_factor

    def transform(self, row: dict):
        return row[self.x_factor] * row[self.y_factor]

    @staticmethod
    def key() -> str:
        return "multiply"


builtins = [Concat, Divide, Multiply]
