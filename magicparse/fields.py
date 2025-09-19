from abc import ABC, abstractmethod
from typing import List

from .builders import Builder
from .type_converters import TypeConverter
from .post_processors import PostProcessor
from .pre_processors import PreProcessor
from .validators import Validator
from .transform import Ok, Result


class Field(ABC):
    def __init__(self, key: str, options: dict) -> None:
        self.key = key
        pre_processors = [
            PreProcessor.build(item) for item in options.get("pre-processors", [])
        ]
        type_converter = TypeConverter.build(options)
        validators = [Validator.build(item) for item in options.get("validators", [])]
        post_processors = [
            PostProcessor.build(item) for item in options.get("post-processors", [])
        ]

        self.optional = options.get("optional", False)

        self.transforms = (
            pre_processors + [type_converter] + validators + post_processors
        )

    def _process_raw_value(self, raw_value: str) -> Result:
        if not raw_value:
            if self.optional:
                return Ok(value=None)
            else:
                raise ValueError(
                    f"{self.key} field is required but the value was empty"
                )
        value = Ok(value=raw_value)
        for transform in self.transforms:
            value = transform.apply(value)
        return value

    @abstractmethod
    def _read_raw_value(self, row: List[str] | dict) -> str:
        pass

    def parse(self, row: List[str] | dict) -> Result:
        raw_value = self._read_raw_value(row)
        return self._process_raw_value(raw_value)

    @abstractmethod
    def error(self, exception: Exception):
        pass

    @classmethod
    def build(cls, options: dict) -> "Field":
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
    def __init__(self, key: str, options: dict) -> None:
        super().__init__(key, options)
        self.column_number = options["column-number"]

    def _read_raw_value(self, row: List[str] | dict) -> str:
        return row[self.column_number - 1]

    def error(self, exception: Exception) -> dict:
        return {
            "column-number": self.column_number,
            "field-key": self.key,
            "error": exception.args[0],
        }


class ColumnarField(Field):
    def __init__(self, key: str, options: dict) -> None:
        super().__init__(key, options)
        self.column_start = options["column-start"]
        self.column_length = options["column-length"]
        self.column_end = self.column_start + self.column_length

    def _read_raw_value(self, row: str | dict) -> str:
        return row[self.column_start : self.column_end]

    def error(self, exception: Exception) -> dict:
        return {
            "column-start": self.column_start,
            "column-length": self.column_length,
            "field-key": self.key,
            "error": exception.args[0],
        }


class ComputedField(Field):
    def __init__(self, key: str, options: dict) -> None:
        super().__init__(key, options)
        self.builder = Builder.build(options["builder"])

    def _read_raw_value(self, row: List[str] | dict) -> str:
        return self.builder.transform(row)

    def error(self, exception: Exception) -> dict:
        return {
            "field-key": self.key,
            "error": exception.args[0],
        }

    @classmethod
    def build(cls, options: dict) -> "ComputedField":
        key = options.pop("key", None)
        if not key:
            raise ValueError("key is required in computed field definition")

        return ComputedField(key, options)
