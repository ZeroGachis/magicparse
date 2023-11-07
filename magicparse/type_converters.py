from datetime import datetime, time
from decimal import Decimal

from .transform import Transform


class TypeConverter(Transform):
    @classmethod
    def build(cls, options) -> "TypeConverter":
        try:
            _type = options["type"]
        except:
            raise ValueError("missing key 'type'")

        try:
            return cls.registry[_type]()
        except:
            raise ValueError(f"invalid type '{_type}'")


class StrConverter(TypeConverter):
    def apply(self, value: str) -> str:
        return value

    @staticmethod
    def key() -> str:
        return "str"


class IntConverter(TypeConverter):
    def apply(self, value: str) -> int:
        try:
            return int(value)
        except:
            raise ValueError(f"value '{value}' is not a valid integer")

    @staticmethod
    def key() -> str:
        return "int"


class DecimalConverter(TypeConverter):
    def apply(self, value: str) -> Decimal:
        try:
            return Decimal(value)
        except:
            raise ValueError(f"value '{value}' is not a valid decimal")

    @staticmethod
    def key() -> str:
        return "decimal"


class TimeConverter(TypeConverter):
    def apply(self, value: str) -> time:
        try:
            parsed = time.fromisoformat(value)
            if parsed.tzinfo is None:
                raise ValueError(f"value '{value}' is a naïve time reprensentation")
            return parsed
        except:
            raise ValueError(f"value '{value}' is not a valid time representation")

    @staticmethod
    def key() -> str:
        return "time"


class DateTimeConverter(TypeConverter):
    def apply(self, value: str) -> datetime:
        try:
            parsed = datetime.fromisoformat(value)
            if parsed.tzinfo is None:
                raise ValueError(f"value '{value}' is a naïve datetime reprensentation")
            return parsed
        except:
            raise ValueError(f"value '{value}' is not a valid datetime representation")

    @staticmethod
    def key() -> str:
        return "datetime"


builtins = [
    StrConverter,
    IntConverter,
    DecimalConverter,
    DateTimeConverter,
    TimeConverter,
]
