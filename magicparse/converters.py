from .transform import Transform
from decimal import Decimal


class Converter(Transform):
    @classmethod
    def build(cls, options) -> "Converter":
        try:
            _type = options["type"]
        except:
            raise ValueError("missing key 'type'")

        try:
            return cls.registry[_type]()
        except:
            raise ValueError(f"invalid type '{_type}'")


class StrConverter(Converter):
    def apply(self, value: str) -> str:
        return value

    def key() -> str:
        return "str"


class IntConverter(Converter):
    def apply(self, value: str) -> int:
        try:
            return int(value)
        except:
            raise ValueError("value is not a valid integer")

    def key() -> str:
        return "int"


class DecimalConverter(Converter):
    def apply(self, value: str) -> Decimal:
        try:
            return Decimal(value)
        except:
            raise ValueError("value is not a valid decimal")

    def key() -> str:
        return "decimal"


builtins = [StrConverter, IntConverter, DecimalConverter]
