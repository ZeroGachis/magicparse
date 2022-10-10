from abc import ABC, abstractmethod
from decimal import Decimal


class Converter(ABC):
    @classmethod
    def build(cls, options) -> "Converter":
        try:
            _type = options["type"]
        except:
            raise ValueError("missing key 'type'")

        try:
            return _types[_type]()
        except:
            raise ValueError(f"invalid type '{_type}'")

    @abstractmethod
    def apply(self, value):
        pass


class StrConverter(Converter):
    def apply(self, value: str) -> str:
        return value


class IntConverter(Converter):
    def apply(self, value: str) -> int:
        try:
            return int(value)
        except:
            raise ValueError("value is not a valid integer")


class DecimalConverter(Converter):
    def apply(self, value: str) -> Decimal:
        try:
            return Decimal(value)
        except:
            raise ValueError("value is not a valid decimal")


_types = {"str": StrConverter, "int": IntConverter, "decimal": DecimalConverter}
