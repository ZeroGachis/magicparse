from abc import ABC, abstractmethod, abstractstaticmethod
import csv
from .fields import Field
from io import StringIO
from typing import Any, Dict, List, Tuple, Union


class Schema(ABC):
    fields: List[Field]
    has_header: bool = False

    def __init__(self, options: Dict[str, Any]) -> None:
        self.fields = [Field.build(item) for item in options["fields"]]

    @abstractmethod
    def get_reader(self, stream: StringIO):
        pass

    @abstractstaticmethod
    def key() -> str:
        pass

    @classmethod
    def build(cls, options: Dict[str, Any]) -> "Schema":
        file_type = options["file_type"]
        schema = cls.registry.get(file_type)
        if schema:
            return schema(options)

        raise ValueError("unknown file type")

    @classmethod
    def register(cls, schema: "Schema") -> None:
        if not hasattr(cls, "registry"):
            cls.registry = {}

        cls.registry[schema.key()] = schema

    def parse(self, data: Union[str, StringIO]) -> Tuple[List[dict], List[dict]]:
        if isinstance(data, str):
            stream = StringIO(data)
        else:
            stream = data

        reader = self.get_reader(stream)

        row_number = 0
        if self.has_header:
            next(reader)
            row_number += 1

        result = []
        errors = []
        for row in reader:
            row_number += 1
            row_is_valid = True
            item = {}
            for field in self.fields:
                try:
                    value = field.read_value(row)
                except Exception as exc:
                    errors.append({"row-number": row_number, **field.error(exc)})
                    row_is_valid = False
                    continue

                item[field.key] = value

            if row_is_valid:
                result.append(item)

        return result, errors


class CsvSchema(Schema):
    def __init__(self, options: Dict[str, Any]) -> None:
        super().__init__(options)
        self.has_header = options.get("has_header", False)
        self.delimiter = options.get("delimiter", ",")

    def get_reader(self, stream: StringIO):
        return csv.reader(stream, delimiter=self.delimiter, quoting=csv.QUOTE_NONE)

    @staticmethod
    def key() -> str:
        return "csv"


class ColumnarSchema(Schema):
    def get_reader(self, stream: StringIO):
        return stream

    @staticmethod
    def key() -> str:
        return "columnar"


builtins = [ColumnarSchema, CsvSchema]
