from abc import ABC, abstractmethod
from typing import Any

from .builders import Builder
from .type_converters import TypeConverter
from .post_processors import PostProcessor
from .pre_processors import PreProcessor
from .validators import Validator
from .transform import Ok, OnError, Result, SkipRow


class Field(ABC):
    def __init__(self, key: str, options: dict[str, Any]) -> None:
        self.key = key
        pre_processors = [PreProcessor.build(item) for item in options.get("pre-processors", [])]
        type_converter = TypeConverter.build(options)
        validators = [Validator.build(item) for item in options.get("validators", [])]
        post_processors = [PostProcessor.build(item) for item in options.get("post-processors", [])]

        self.optional = options.get("optional", False)

        self.transforms = pre_processors + [type_converter] + validators + post_processors

    def _process_raw_value(self, raw_value: str) -> Result:
        if not raw_value:
            if self.optional:
                return Ok(value=None)
            else:
                raise ValueError(f"{self.key} field is required but the value was empty")
        for transform in self.transforms:
            try:
                raw_value = transform.apply(raw_value)
            except Exception as exc:
                if transform.on_error == OnError.SKIP_ROW.value:
                    return SkipRow(exception=exc)
                raise
        return Ok(value=raw_value)

    @abstractmethod
    def _read_raw_value(self, row: Any) -> str:
        pass

    def parse(self, row: str | list[str] | dict[str, Any]) -> Result:
        raw_value = self._read_raw_value(row)
        return self._process_raw_value(raw_value)

    @abstractmethod
    def error(self, exception: Exception) -> dict[str, Any]:
        pass

    @classmethod
    def build(cls, options: dict[str, Any]) -> "Field":
        options = options.copy()
        key = options.pop("key", None)
        if not key:
            raise ValueError("key is required in field definition")

        column_number = options.get("column-number")
        if column_number:
            return CsvField(key, options)

        column_start = options.get("column-start")
        column_length = options.get("column-length")
        if column_start is not None and column_length is not None:
            return ColumnarField(key, options)

        raise ValueError(f"missing field position for field: '{key}'")


class CsvField(Field):
    def __init__(self, key: str, options: dict[str, Any]) -> None:
        super().__init__(key, options)
        self.column_number = int(options["column-number"])

    def _read_raw_value(self, row: list[str]) -> str:
        return row[self.column_number - 1]

    def error(self, exception: Exception) -> dict[str, Any]:
        return {
            "column-number": self.column_number,
            "field-key": self.key,
            "error": exception.args[0],
        }


class ColumnarField(Field):
    def __init__(self, key: str, options: dict[str, Any]) -> None:
        super().__init__(key, options)
        self.column_start = int(options["column-start"])
        self.column_length = int(options["column-length"])
        self.column_end = self.column_start + self.column_length

    def _read_raw_value(self, row: str) -> str:
        return row[self.column_start : self.column_end]

    def error(self, exception: Exception) -> dict[str, Any]:
        return {
            "column-start": self.column_start,
            "column-length": self.column_length,
            "field-key": self.key,
            "error": exception.args[0],
        }


class ComputedField(Field):
    def __init__(self, key: str, options: dict[str, Any]) -> None:
        super().__init__(key, options)
        self.builder = Builder.build(options["builder"])

    def _read_raw_value(self, row: dict[str, Any]) -> str:
        return self.builder.apply(row)

    def error(self, exception: Exception) -> dict[str, Any]:
        return {
            "field-key": self.key,
            "error": exception.args[0],
        }

    @classmethod
    def build(cls, options: dict[str, Any]) -> "ComputedField":
        key = options.pop("key", None)
        if not key:
            raise ValueError("key is required in computed field definition")

        return ComputedField(key, options)
