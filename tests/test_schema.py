from decimal import Decimal
from unittest.mock import Mock
from magicparse import Schema
from magicparse.schema import ColumnarSchema, CsvSchema
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
        rows, errors = schema.parse(b"1\na\n2")
        assert rows == [{"age": 1}, {"age": 2}]
        assert errors == [
            {
                "row-number": 2,
                "column-number": 1,
                "field-key": "age",
                "error": "value is not a valid integer",
            }
        ]


class TestStreamParse:
    def test_with_no_data(self):
        on_valid_row = Mock()
        on_error_row = Mock()
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [{"key": "name", "type": "str", "column-number": 1}],
            }
        )
        schema.stream_parse(b"", on_valid_row, on_error_row)
        assert not on_valid_row.called
        assert not on_error_row.called

    def test_with_no_field_definition(self):
        on_valid_row = Mock()
        on_error_row = Mock()
        schema = Schema.build({"file_type": "csv", "fields": []})
        schema.stream_parse(b"a,b,c\n", on_valid_row, on_error_row)
        on_valid_row.assert_called_once_with(
            index=0, parsed_row={}, raw_data=b"a,b,c\n"
        )
        assert not on_error_row.called

    def test_without_header(self):
        on_valid_row = Mock()
        on_error_row = Mock()
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [{"key": "name", "type": "str", "column-number": 1}],
            }
        )
        schema.stream_parse(b"1\n", on_valid_row, on_error_row)
        on_valid_row.assert_called_once_with(
            index=0, parsed_row={"name": "1"}, raw_data=b"1\n"
        )
        assert not on_error_row.called

    def test_with_header(self):
        on_valid_row = Mock()
        on_error_row = Mock()
        schema = Schema.build(
            {
                "file_type": "csv",
                "has_header": True,
                "fields": [{"key": "name", "type": "str", "column-number": 1}],
            }
        )
        schema.stream_parse(b"column_name\n1\n", on_valid_row, on_error_row)

        on_valid_row.assert_called_once_with(
            index=1, parsed_row={"name": "1"}, raw_data=b"1\n"
        )
        assert not on_error_row.called

    def test_multiple_lines(self):
        on_valid_row = Mock()
        on_error_row = Mock()
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [{"key": "name", "type": "str", "column-number": 1}],
            }
        )
        schema.stream_parse(b"1\n2\n", on_valid_row, on_error_row)
        assert on_valid_row.call_count == 2
        on_valid_row.assert_any_call(index=0, parsed_row={"name": "1"}, raw_data=b"1\n")
        on_valid_row.assert_any_call(index=1, parsed_row={"name": "2"}, raw_data=b"2\n")
        assert not on_error_row.called

    def test_error_display_row_number(self):
        on_valid_row = Mock()
        on_error_row = Mock()
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [{"key": "age", "type": "int", "column-number": 1}],
            }
        )
        schema.stream_parse(b"a", on_valid_row, on_error_row)
        assert not on_valid_row.called
        on_error_row.assert_called_once_with(
            errors_info=[
                {
                    "row-number": 0,
                    "column-number": 1,
                    "field-key": "age",
                    "error": "value is not a valid integer",
                }
            ],
            raw_data=b"a",
        )

    def test_errors_do_not_halt_parsing(self):
        on_valid_row = Mock()
        on_error_row = Mock()
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [{"key": "age", "type": "int", "column-number": 1}],
            }
        )
        schema.stream_parse(b"1\na\n2\n", on_valid_row, on_error_row)
        assert on_valid_row.call_count == 2
        on_valid_row.assert_any_call(index=0, parsed_row={"age": 1}, raw_data=b"1\n")
        on_valid_row.assert_any_call(index=2, parsed_row={"age": 2}, raw_data=b"2\n")
        on_error_row.assert_called_once_with(
            errors_info=[
                {
                    "row-number": 1,
                    "column-number": 1,
                    "field-key": "age",
                    "error": "value is not a valid integer",
                }
            ],
            raw_data=b"a\n",
        )


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
        rows, errors = schema.parse(b"1\na\n2")
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
                "has_header": True,
                "fields": [{"key": "column_1", "type": "decimal", "column-number": 1}],
            }
        )
        rows, errors = schema.parse(b'column_1\n"6.66"')
        assert rows == [{"column_1": Decimal("6.66")}]
        assert not errors


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
