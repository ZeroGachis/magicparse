import codecs
from abc import ABC, abstractmethod
import csv
from .fields import Field, ComputedField
from io import BytesIO
from typing import Any, Dict, List, Tuple, Union, Iterable


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

        for item, row_errors in self.stream_parse(data):
            if row_errors:
                errors.extend(row_errors)
            else:
                items.append(item)

        return items, errors

    def stream_parse(
        self, data: Union[bytes, BytesIO]
    ) -> Iterable[Tuple[dict, list[dict]]]:
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
            if any(row):
                errors = []
                item = {}
                for field in self.fields:
                    try:
                        value = field.read_value(row)
                    except Exception as exc:
                        errors.append({"row-number": row_number, **field.error(exc)})
                        continue

                    item[field.key] = value

                for computed_field in self.computed_fields:
                    try:
                        value = computed_field.read_value(item)
                    except Exception as exc:
                        errors.append(
                            {"row-number": row_number, **computed_field.error(exc)}
                        )
                        continue

                    item[computed_field.key] = value

                yield item, errors


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
