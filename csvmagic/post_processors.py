from abc import ABC, abstractmethod
from decimal import Decimal
from typing import TypeVar


T = TypeVar("T")


class PostProcessor(ABC):
    @classmethod
    def build(cls, options: dict) -> "PostProcessor":
        post_processor = _post_processors[options["name"]]

        if "parameters" in options:
            return post_processor(**options["parameters"])
        else:
            return post_processor()

    @abstractmethod
    def apply(self, value: T) -> T:
        pass


class Divide:
    Number = TypeVar("Number", int, float, Decimal)

    def __init__(self, denominator: int) -> None:
        self.denominator = denominator

    def apply(self, value: Number) -> Number:
        return value / self.denominator


_post_processors = {
    "divide": Divide,
}
