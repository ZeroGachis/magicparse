from decimal import Decimal
from .transform import Transform
import re


class Validator(Transform):
    @classmethod
    def build(cls, options: dict) -> "Validator":
        try:
            name = options["name"]
        except:
            raise ValueError("validator must have a 'name' key")

        try:
            validator = cls.registry[name]
        except:
            raise ValueError(f"invalid validator '{name}'")

        if "parameters" in options:
            return validator(**options["parameters"])
        else:
            return validator()


class RegexMatches(Validator):
    def __init__(self, pattern: str) -> None:
        self.pattern = re.compile(pattern)

    def apply(self, value: str) -> str:
        if re.match(self.pattern, value):
            return value

        raise ValueError(f"string does not match regex '{self.pattern.pattern}'")

    @staticmethod
    def key() -> str:
        return "regex-matches"


class GreaterThan(Validator):
    def __init__(self, threshold: float) -> None:
        self.threshold = Decimal(threshold)

    def apply(self, value: Decimal) -> Decimal:
        if value > self.threshold:
            return value
        raise ValueError(f"value must be greater than {self.threshold}")

    @staticmethod
    def key() -> str:
        return "greater-than"


builtins = [GreaterThan, RegexMatches]
