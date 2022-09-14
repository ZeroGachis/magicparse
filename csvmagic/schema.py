from abc import ABC, abstractmethod
import csv
from io import StringIO
from typing import List
from .fields import Field, CsvField, ColumnarField


class Schema(ABC):
    fields: List[Field]
    has_header: bool

    @abstractmethod
    def get_reader(self, data: str):
        pass

    @classmethod
    def build(self, options: dict) -> "Schema":
        if options["file_type"] == "csv":
            return CsvSchema(options)
        elif options["file_type"] == "columnar":
            return ColumnarSchema(options)
        else:
            raise ValueError("unknown file type")


class CsvSchema(Schema):
    def __init__(self, schema: Schema) -> None:
        self.has_header = schema["has_header"]
        self.delimiter = schema["delimiter"]
        self.fields = [CsvField(field) for field in schema["fields"]]

    def get_reader(self, data: str):
        return csv.reader(
            StringIO(data), delimiter=self.delimiter, quoting=csv.QUOTE_NONE
        )


class ColumnarSchema(Schema):
    def __init__(self, schema: Schema) -> None:
        self.has_header = False
        self.fields = [ColumnarField(field) for field in schema["fields"]]

    def get_reader(self, data: str):
        return StringIO(data)
