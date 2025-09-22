from decimal import Decimal
from typing import Any
from .transform import Transform, OnError
import re


class Validator(Transform):
    registry = dict[str, type["Validator"]]()

    @classmethod
    def build(cls, options: dict[str, Any]) -> "Validator":
        try:
            name = options["name"]
        except:
            raise ValueError("validator must have a 'name' key")

        try:
            validator = cls.registry[name]
        except:
            raise ValueError(f"invalid validator '{name}'")

        assert issubclass(validator, Validator)

        on_error = options.setdefault("on-error", OnError.RAISE)
        if "parameters" in options:
            return validator(on_error=on_error, **options["parameters"])
        else:
            return validator(on_error=on_error)


class RegexMatches(Validator):
    def __init__(self, on_error: OnError, pattern: str) -> None:
        super().__init__(on_error)
        self.pattern = re.compile(pattern)

    def apply(self, value: str) -> str | None:
        if re.match(self.pattern, value):
            return value

        raise ValueError(f"string does not match regex '{self.pattern.pattern}'")

    @staticmethod
    def key() -> str:
        return "regex-matches"


class GreaterThan(Validator):
    def __init__(self, on_error: OnError, threshold: float) -> None:
        super().__init__(on_error)
        self.threshold = Decimal(threshold)

    def apply(self, value: Decimal) -> Decimal:
        if value > self.threshold:
            return value
        raise ValueError(f"value must be greater than {self.threshold}")

    @staticmethod
    def key() -> str:
        return "greater-than"


class NotNullOrEmpty(Validator):
    def apply(self, value: str) -> str:
        if not value:
            raise ValueError("value must not be null or empty")
        return value

    @staticmethod
    def key() -> str:
        return "not-null-or-empty"


builtins = [GreaterThan, RegexMatches, NotNullOrEmpty]
