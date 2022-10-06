from csvmagic import Schema
from csvmagic.schema import ColumnarSchema, CsvSchema
from csvmagic.fields import ColumnarField, CsvField
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
        rows, errors = schema.parse("")
        assert not rows
        assert not errors

    def test_with_no_field_definition(self):
        schema = Schema.build({"file_type": "csv", "fields": []})
        rows, errors = schema.parse("a,b,c")
        assert rows == [{}]
        assert not errors

    def test_without_header(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [{"key": "name", "type": "str", "column-number": 1}],
            }
        )
        rows, errors = schema.parse("1")
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
        rows, errors = schema.parse("column_name\n1")
        assert rows == [{"name": "1"}]
        assert not errors

    def test_error_display_row_number(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [{"key": "age", "type": "int", "column-number": 1}],
            }
        )
        rows, errors = schema.parse("a")
        assert not rows
        assert errors == [
            {
                "row-number": 1,
                "column-number": 1,
                "field-key": "age",
                "error": "value is not a valid integer",
            }
        ]

    def test_errors_do_not_halt_parsing(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [{"key": "age", "type": "int", "column-number": 1}],
            }
        )
        rows, errors = schema.parse("1\na\n2")
        assert rows == [{"age": 1}, {"age": 2}]
        assert errors == [
            {
                "row-number": 2,
                "column-number": 1,
                "field-key": "age",
                "error": "value is not a valid integer",
            }
        ]


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
        rows, errors = schema.parse("")
        assert not rows
        assert not errors

    def test_with_no_field_definition(self):
        schema = Schema.build({"file_type": "columnar", "fields": []})
        rows, errors = schema.parse("a")
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
        rows, errors = schema.parse("1")
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
        rows, errors = schema.parse("a")
        assert not rows
        assert errors == [
            {
                "row-number": 1,
                "column-start": 0,
                "column-length": 1,
                "field-key": "age",
                "error": "value is not a valid integer",
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
        rows, errors = schema.parse("1\na\n2")
        assert rows == [{"age": 1}, {"age": 2}]
        assert errors == [
            {
                "row-number": 2,
                "column-start": 0,
                "column-length": 1,
                "field-key": "age",
                "error": "value is not a valid integer",
            }
        ]
