from abc import ABC, abstractmethod
from decimal import Decimal


class Converter(ABC):
    @classmethod
    def build(cls, options) -> "Converter":
        return _types[options["type"]]()

    @abstractmethod
    def apply(self, value):
        pass


class StrConverter(Converter):
    def apply(self, value: str) -> str:
        return value


class IntConverter(Converter):
    def apply(self, value: str) -> int:
        return int(value)


class DecimalConverter(Converter):
    def apply(self, value: str) -> Decimal:
        return Decimal(value)


_types = {"str": StrConverter, "int": IntConverter, "decimal": DecimalConverter}
