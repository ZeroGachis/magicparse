import codecs
from abc import ABC, abstractmethod
import csv
from dataclasses import dataclass

from magicparse.transform import SkipRow
from .fields import Field, ComputedField
from io import BytesIO
from typing import Any, Dict, List, Union, Iterable


@dataclass(frozen=True, slots=True)
class RowParsed:
    row_number: int
    values: dict


@dataclass(frozen=True, slots=True)
class RowSkipped:
    row_number: int
    errors: list[dict]


@dataclass(frozen=True, slots=True)
class RowFailed:
    row_number: int
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

    def parse(
        self, data: Union[bytes, BytesIO]
    ) -> List[RowParsed] | List[RowSkipped] | List[RowFailed]:
        return list(self.stream_parse(data))

    def stream_parse(
        self, data: Union[bytes, BytesIO]
    ) -> Iterable[RowParsed | RowSkipped | RowFailed]:
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

            fields = self.process_fields(self.fields, row, row_number)
            if not isinstance(fields, RowParsed):
                yield fields
                continue

            computed_fields = self.process_fields(
                self.computed_fields, fields.values, row_number
            )
            if not isinstance(computed_fields, RowParsed):
                yield computed_fields
                continue

            yield RowParsed(row_number, {**fields.values, **computed_fields.values})

    def process_fields(
        self, fields: List[Field], row: List[str], row_number: int
    ) -> RowParsed | RowSkipped | RowFailed:
        item = {}
        errors = []
        skip_row = False
        for field in fields:
            try:
                parsed_value = field.parse(row)
            except Exception as exc:
                errors.append(field.error(exc))
                continue

            if isinstance(parsed_value, SkipRow):
                skip_row = True
                errors.append(field.error(parsed_value.exception))
                continue

            item[field.key] = parsed_value.value

        if errors:
            return (
                RowSkipped(row_number, errors)
                if skip_row
                else RowFailed(row_number, errors)
            )

        return RowParsed(row_number, item)


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
