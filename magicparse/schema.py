import codecs
from abc import ABC, abstractmethod
import csv
from .fields import Field
from io import BytesIO
from typing import Any, Dict, List, Tuple, Union, Iterable


class Schema(ABC):
    fields: List[Field]
    encoding: str
    has_headers: bool

    def __init__(self, options: Dict[str, Any]) -> None:
        self.fields = [Field.build(item) for item in options["fields"]]

        self.has_header = options.get("has_header", False)
        self.encoding = options.get("encoding", "utf-8")

    @abstractmethod
    def get_reader(self, stream: BytesIO) -> Iterable:
        pass

    @staticmethod
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

    def parse(self, data: Union[bytes, BytesIO]) -> Tuple[List[dict], List[dict]]:
        if isinstance(data, bytes):
            stream = BytesIO(data)
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
        self.delimiter = options.get("delimiter", ",")

    def get_reader(self, stream: BytesIO) -> Iterable[List[str]]:
        stream_reader = codecs.getreader(self.encoding)
        stream_content = stream_reader(stream)

        return csv.reader(
            stream_content, delimiter=self.delimiter, quoting=csv.QUOTE_NONE
        )

    @staticmethod
    def key() -> str:
        return "csv"


class ColumnarSchema(Schema):
    def get_reader(self, stream: BytesIO) -> Iterable[str]:
        stream_reader = codecs.getreader(self.encoding)
        return stream_reader(stream)

    @staticmethod
    def key() -> str:
        return "columnar"


builtins = [ColumnarSchema, CsvSchema]
