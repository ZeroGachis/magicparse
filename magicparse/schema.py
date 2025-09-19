import codecs
from abc import ABC, abstractmethod
import csv
from dataclasses import dataclass

from magicparse.transform import SkipRow
from .fields import Field, ComputedField
from io import BytesIO
from typing import Any, Dict, List, Tuple, Union, Iterable


@dataclass(frozen=True, slots=True)
class ParsedRow:
    row_number: int
    values: dict
    errors: list[dict]


class Schema(ABC):
    fields: List[Field]
    encoding: str
    has_headers: bool

    def __init__(self, options: Dict[str, Any]) -> None:
        self.fields = [Field.build(item) for item in options["fields"]]
        self.computed_fields = [
            ComputedField.build(item) for item in options.get("computed-fields", [])
        ]

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
        items = []
        errors = []

        for parsed_row in self.stream_parse(data):
            if parsed_row.errors:
                errors.extend(parsed_row.errors)
            else:
                items.append(parsed_row.values)

        return items, errors

    def stream_parse(self, data: Union[bytes, BytesIO]) -> Iterable[ParsedRow]:
        if isinstance(data, bytes):
            stream = BytesIO(data)
        else:
            stream = data

        reader = self.get_reader(stream)

        row_number = 0
        if self.has_header:
            next(reader)
            row_number += 1

        for row in reader:
            row_number += 1
            if not any(row):
                continue

            parsed_fields = self.process_fields(self.fields, row, row_number)
            if isinstance(parsed_fields, SkipRow):
                continue

            computed_fields = self.process_fields(
                self.computed_fields, parsed_fields.values, row_number
            )
            if isinstance(computed_fields, SkipRow):
                continue

            yield ParsedRow(
                row_number,
                {**parsed_fields.values, **computed_fields.values},
                parsed_fields.errors + computed_fields.errors,
            )

    def process_fields(
        self, fields: List[Field], row: List[str], row_number: int
    ) -> ParsedRow | SkipRow:
        item = {}
        errors = []
        for field in fields:
            try:
                parsed_value = field.parse(row)

            except Exception as exc:
                errors.append({"row-number": row_number, **field.error(exc)})
                continue

            if isinstance(parsed_value, SkipRow):
                return parsed_value

            item[field.key] = parsed_value.value

        return ParsedRow(row_number, item, errors)


class CsvSchema(Schema):
    def __init__(self, options: Dict[str, Any]) -> None:
        super().__init__(options)
        self.delimiter = options.get("delimiter", ",")
        self.quotechar = options.get("quotechar", None)

    def get_reader(self, stream: BytesIO) -> Iterable[List[str]]:
        stream_reader = codecs.getreader(self.encoding)
        stream_content = stream_reader(stream)
        csv_quoting = csv.QUOTE_NONE
        if self.quotechar:
            csv_quoting = csv.QUOTE_MINIMAL
        return csv.reader(
            stream_content,
            delimiter=self.delimiter,
            quoting=csv_quoting,
            quotechar=self.quotechar,
        )

    @staticmethod
    def key() -> str:
        return "csv"


class ColumnarSchema(Schema):
    def get_reader(self, stream: BytesIO) -> Iterable[str]:
        stream_reader_factory = codecs.getreader(self.encoding)
        stream_reader = stream_reader_factory(stream)
        while True:
            line = stream_reader.readline(None, False)
            if not line:
                break
            yield line

    @staticmethod
    def key() -> str:
        return "columnar"


builtins = [ColumnarSchema, CsvSchema]
