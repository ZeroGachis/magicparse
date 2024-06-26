from decimal import Decimal

from magicparse import Schema
from magicparse.schema import ColumnarSchema, CsvSchema, ParsedRow
from magicparse.fields import ColumnarField, CsvField
import pytest
from unittest import TestCase


class TestBuild(TestCase):
    def test_default_csv_schema(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [{"key": "name", "type": "str", "column-number": 1}],
            }
        )
        assert isinstance(schema, CsvSchema)
        assert not schema.has_header
        assert schema.delimiter == ","
        assert len(schema.fields) == 1 and isinstance(schema.fields[0], CsvField)

    def test_csv_with_header(self):
        schema = Schema.build({"file_type": "csv", "has_header": True, "fields": []})
        assert isinstance(schema, CsvSchema)
        assert schema.has_header

    def test_csv_with_hdelimiter(self):
        schema = Schema.build({"file_type": "csv", "delimiter": ";", "fields": []})
        assert isinstance(schema, CsvSchema)
        assert schema.delimiter == ";"

    def test_columnar(self):
        schema = Schema.build(
            {
                "file_type": "columnar",
                "fields": [
                    {
                        "key": "name",
                        "type": "str",
                        "column-start": 0,
                        "column-length": 1,
                    }
                ],
            }
        )
        assert isinstance(schema, ColumnarSchema)
        assert not schema.has_header
        assert len(schema.fields) == 1 and isinstance(schema.fields[0], ColumnarField)

    def test_unknwown(self):
        with pytest.raises(ValueError, match="unknown file type"):
            Schema.build({"file_type": "anything", "fields": []})


class TestCsvParse(TestCase):
    def test_with_no_data(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [{"key": "name", "type": "str", "column-number": 1}],
            }
        )
        rows, errors = schema.parse(b"")
        assert not rows
        assert not errors

    def test_with_no_field_definition(self):
        schema = Schema.build({"file_type": "csv", "fields": []})
        rows, errors = schema.parse(b"a,b,c")
        assert rows == [{}]
        assert not errors

    def test_without_header(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [{"key": "name", "type": "str", "column-number": 1}],
            }
        )
        rows, errors = schema.parse(b"1")
        assert rows == [{"name": "1"}]
        assert not errors

    def test_with_header(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "has_header": True,
                "fields": [{"key": "name", "type": "str", "column-number": 1}],
            }
        )
        rows, errors = schema.parse(b"column_name\n1")
        assert rows == [{"name": "1"}]
        assert not errors

    def test_error_display_row_number(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [{"key": "age", "type": "int", "column-number": 1}],
            }
        )
        rows, errors = schema.parse(b"a")
        assert not rows
        assert errors == [
            {
                "row-number": 1,
                "column-number": 1,
                "field-key": "age",
                "error": "value 'a' is not a valid integer",
            }
        ]

    def test_errors_do_not_halt_parsing(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [{"key": "age", "type": "int", "column-number": 1}],
            }
        )
        rows, errors = schema.parse(b"1\na\n2")
        assert rows == [{"age": 1}, {"age": 2}]
        assert errors == [
            {
                "row-number": 2,
                "column-number": 1,
                "field-key": "age",
                "error": "value 'a' is not a valid integer",
            }
        ]

    def test_parse_should_skip_empty_lines(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [{"key": "name", "type": "str", "column-number": 1}],
            }
        )
        rows, errors = schema.parse(
            b"""1

"""
        )
        assert rows == [{"name": "1"}]
        assert not errors


class TestColumnarParse(TestCase):
    def test_with_no_data(self):
        schema = Schema.build(
            {
                "file_type": "columnar",
                "fields": [
                    {
                        "key": "name",
                        "type": "str",
                        "column-start": 0,
                        "column-length": 1,
                    }
                ],
            }
        )
        rows, errors = schema.parse(b"")
        assert not rows
        assert not errors

    def test_with_no_field_definition(self):
        schema = Schema.build({"file_type": "columnar", "fields": []})
        rows, errors = schema.parse(b"a")
        assert rows == [{}]
        assert not errors

    def test_parse(self):
        schema = Schema.build(
            {
                "file_type": "columnar",
                "fields": [
                    {
                        "key": "name",
                        "type": "str",
                        "column-start": 0,
                        "column-length": 1,
                    }
                ],
            }
        )
        rows, errors = schema.parse(b"1")
        assert rows == [{"name": "1"}]
        assert not errors

    def test_error_display_row_number(self):
        schema = Schema.build(
            {
                "file_type": "columnar",
                "fields": [
                    {"key": "age", "type": "int", "column-start": 0, "column-length": 1}
                ],
            }
        )
        rows, errors = schema.parse(b"a")
        assert not rows
        assert errors == [
            {
                "row-number": 1,
                "column-start": 0,
                "column-length": 1,
                "field-key": "age",
                "error": "value 'a' is not a valid integer",
            }
        ]

    def test_errors_do_not_halt_parsing(self):
        schema = Schema.build(
            {
                "file_type": "columnar",
                "fields": [
                    {"key": "age", "type": "int", "column-start": 0, "column-length": 1}
                ],
            }
        )
        rows, errors = schema.parse(b"1\na\n2")
        assert rows == [{"age": 1}, {"age": 2}]
        assert errors == [
            {
                "row-number": 2,
                "column-start": 0,
                "column-length": 1,
                "field-key": "age",
                "error": "value 'a' is not a valid integer",
            }
        ]

    def test_parse_should_skip_empty_lines(self):
        schema = Schema.build(
            {
                "file_type": "columnar",
                "fields": [
                    {
                        "key": "name",
                        "type": "str",
                        "column-start": 0,
                        "column-length": 8,
                    }
                ],
            }
        )
        rows, errors = schema.parse(
            b"""8013109C

"""
        )
        assert rows == [{"name": "8013109C"}]
        assert not errors


class TestQuotingSetting(TestCase):
    def test_no_quote(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "has_header": True,
                "fields": [{"key": "column_1", "type": "decimal", "column-number": 1}],
            }
        )
        rows, errors = schema.parse(b"column_1\n6.66")
        assert rows == [{"column_1": Decimal("6.66")}]
        assert not errors

    def test_single_quote(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "quotechar": "'",
                "has_header": True,
                "fields": [{"key": "column_1", "type": "decimal", "column-number": 1}],
            }
        )
        rows, errors = schema.parse(b"column_1\n'6.66'")
        assert rows == [{"column_1": Decimal("6.66")}]
        assert not errors

    def test_double_quote(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "quotechar": '"',
                "has_header": True,
                "fields": [{"key": "column_1", "type": "decimal", "column-number": 1}],
            }
        )
        rows, errors = schema.parse(b'column_1\n"6.66"')
        assert rows == [{"column_1": Decimal("6.66")}]
        assert not errors

    def test_asymetrical_quote(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "has_header": True,
                "fields": [{"key": "column_1", "type": "str", "column-number": 1}],
            }
        )
        rows, errors = schema.parse(b'column_1\n"test ""quoting""')
        assert rows == [{"column_1": '"test ""quoting""'}]


class TestRegister(TestCase):
    class PipedSchema(Schema):
        @staticmethod
        def key() -> str:
            return "piped"

        def get_reader(self, stream):
            for item in stream.read().split("|"):
                yield [item]

    def test_register(self):
        Schema.register(self.PipedSchema)

        schema = Schema.build(
            {
                "file_type": "piped",
                "fields": [{"key": "name", "type": "str", "column-number": 1}],
            }
        )
        assert isinstance(schema, self.PipedSchema)


class TestSteamParse(TestCase):
    def test_stream_parse_errors_do_not_halt_parsing(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [{"key": "age", "type": "int", "column-number": 1}],
            }
        )
        rows = list(schema.stream_parse(b"1\na\n2"))
        assert rows == [
            ParsedRow(row_number=1, values={"age": 1}, errors=[]),
            ParsedRow(
                row_number=2,
                values={},
                errors=[
                    {
                        "row-number": 2,
                        "column-number": 1,
                        "field-key": "age",
                        "error": "value 'a' is not a valid integer",
                    }
                ],
            ),
            ParsedRow(row_number=3, values={"age": 2}, errors=[]),
        ]

    def test_stream_parse_with_header_first_row_number_is_2(self):
        schema = Schema.build(
            {
                "has_header": True,
                "file_type": "csv",
                "fields": [{"key": "age", "type": "int", "column-number": 1}],
            }
        )
        rows = list(schema.stream_parse(b"My age\n1"))
        assert len(rows) == 1
        assert rows[0].row_number == 2

    def test_stream_parse_without_header_first_row_number_is_1(self):
        schema = Schema.build(
            {
                "has_header": False,
                "file_type": "csv",
                "fields": [{"key": "age", "type": "int", "column-number": 1}],
            }
        )
        rows = list(schema.stream_parse(b"1"))
        assert len(rows) == 1
        assert rows[0].row_number == 1
