from abc import abstractmethod
from datetime import datetime, time
from decimal import Decimal
from typing import Any, cast

from .transform import ParsingTransform
from .transform import OnError


class TypeConverter(ParsingTransform):
    registry = dict[str, type["TypeConverter"]]()

    def __init__(self, nullable: bool, on_error: OnError) -> None:
        super().__init__(on_error)
        self.nullable = nullable

    def apply(self, value: str | None) -> Any | None:
        if value is None:
            if self.nullable:
                return None
            else:
                raise ValueError("type is non nullable")

        return self.convert(value)

    @abstractmethod
    def convert(self, value: str) -> Any:
        pass

    @classmethod
    def build(cls, options: dict[str, Any]) -> "ParsingTransform":
        try:
            type = cast(str | dict[str, Any], options["type"])
            if isinstance(type, str):
                key = type
                type = {}
            else:
                key = type.pop("key")
        except:
            raise ValueError("missing key 'type'")

        nullable = type.pop("nullable", False)
        on_error = type.pop("on-error", OnError.RAISE)
        try:
            return cls.registry[key](nullable, on_error, **type)
        except Exception as e:
            raise ValueError(f"invalid type '{key}': {e}")


class StrConverter(TypeConverter):
    def convert(self, value: str) -> str:
        return value

    @staticmethod
    def key() -> str:
        return "str"


class IntConverter(TypeConverter):
    def convert(self, value: str) -> int:
        try:
            return int(value)
        except:
            raise ValueError(f"value '{value}' is not a valid integer")

    @staticmethod
    def key() -> str:
        return "int"


class DecimalConverter(TypeConverter):
    def convert(self, value: str) -> Decimal:
        try:
            return Decimal(value)
        except:
            raise ValueError(f"value '{value}' is not a valid decimal")

    @staticmethod
    def key() -> str:
        return "decimal"


class TimeConverter(TypeConverter):
    def convert(self, value: str) -> time:
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
    def convert(self, value: str) -> datetime:
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
