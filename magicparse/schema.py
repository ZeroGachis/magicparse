from abc import ABC, abstractmethod
import csv
from .fields import Field, CsvField, ColumnarField
from io import StringIO
from typing import Any, Dict, List, Tuple


class Schema(ABC):
    fields: List[Field]
    has_header: bool

    @abstractmethod
    def get_reader(self, data: str):
        pass

    @classmethod
    def build(self, options: Dict[str, Any]) -> "Schema":
        if options["file_type"] == "csv":
            return CsvSchema(options)
        elif options["file_type"] == "columnar":
            return ColumnarSchema(options)
        else:
            raise ValueError("unknown file type")

    def parse(self, data: str) -> Tuple[List[dict], List[dict]]:
        reader = self.get_reader(data)

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
    def __init__(self, schema: Dict[str, Any]) -> None:
        self.has_header = schema.get("has_header", False)
        self.delimiter = schema.get("delimiter", ",")
        self.fields = [CsvField(field) for field in schema["fields"]]

    def get_reader(self, data: str):
        return csv.reader(
            StringIO(data), delimiter=self.delimiter, quoting=csv.QUOTE_NONE
        )


class ColumnarSchema(Schema):
    def __init__(self, schema: Dict[str, Any]) -> None:
        self.has_header = False
        self.fields = [ColumnarField(field) for field in schema["fields"]]

    def get_reader(self, data: str):
        return StringIO(data)