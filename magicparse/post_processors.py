from .transform import Transform
from decimal import Decimal
from typing import TypeVar


class PostProcessor(Transform):
    @classmethod
    def build(cls, options: dict) -> "PostProcessor":
        try:
            name = options["name"]
        except:
            raise ValueError("post-processor must have a 'name' key")

        try:
            post_processor = cls.registry[name]
        except:
            raise ValueError(f"invalid post-processor '{name}'")

        if "parameters" in options:
            return post_processor(**options["parameters"])
        else:
            return post_processor()


class Divide(PostProcessor):
    Number = TypeVar("Number", int, float, Decimal)

    def __init__(self, denominator: int) -> None:
        if denominator <= 0:
            raise ValueError(
                "post-processor 'divide': "
                "'denominator' parameter must be a positive integer"
            )

        self.denominator = denominator

    def apply(self, value: Number) -> Number:
        return value / self.denominator

    @staticmethod
    def key() -> str:
        return "divide"


class Round(PostProcessor):
    Number = TypeVar("Number", int, float, Decimal)

    def __init__(self, precision: int) -> None:
        if precision < 0:
            raise ValueError(
                "post-processor 'round': "
                "'precision' parameter must be a positive or zero integer"
            )

        self.precision = precision

    def apply(self, value: Number) -> Number:
        return round(value, self.precision)

    @staticmethod
    def key() -> str:
        return "round"


builtins = [Divide, Round]
