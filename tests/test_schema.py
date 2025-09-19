from decimal import Decimal
from typing import Any

from magicparse import Schema
from magicparse.post_processors import PostProcessor
from magicparse.pre_processors import PreProcessor
from magicparse.schema import (
    ColumnarSchema, CsvSchema, RowParsed, RowFailed, RowSkipped
)
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
        rows = schema.parse(b"")
        assert rows == []

    def test_with_no_field_definition(self):
        schema = Schema.build({"file_type": "csv", "fields": []})
        rows = schema.parse(b"a,b,c")
        assert rows == [RowParsed(row_number=1, values={})]

    def test_without_header(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [{"key": "name", "type": "str", "column-number": 1}],
            }
        )
        rows = schema.parse(b"1")
        assert rows == [RowParsed(row_number=1, values={"name": "1"})]

    def test_with_header(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "has_header": True,
                "fields": [{"key": "name", "type": "str", "column-number": 1}],
            }
        )
        rows = schema.parse(b"column_name\n1")
        assert rows == [RowParsed(row_number=2, values={"name": "1"})]

    def test_error_display_row_number(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [{"key": "age", "type": "int", "column-number": 1}],
            }
        )
        rows = schema.parse(b"a")
        assert rows == [
            RowFailed(row_number=1, errors=[{
                "column-number": 1,
                "field-key": "age",
                "error": "value 'a' is not a valid integer",
            }])
        ]

    def test_errors_do_not_halt_parsing(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [{"key": "age", "type": "int", "column-number": 1}],
            }
        )
        rows = schema.parse(b"1\na\n2")
        assert rows == [
            RowParsed(row_number=1, values={"age": 1}),
            RowFailed(row_number=2, errors=[{
                "column-number": 1,
                "field-key": "age",
                "error": "value 'a' is not a valid integer",
            }]),
            RowParsed(row_number=3, values={"age": 2}),
        ]

    def test_parse_should_skip_empty_lines(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [{"key": "name", "type": "str", "column-number": 1}],
            }
        )
        rows = schema.parse(
            b"""1

"""
        )
        assert rows == [RowParsed(row_number=1, values={"name": "1"})]


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
        rows = schema.parse(b"")
        assert rows == []

    def test_with_no_field_definition(self):
        schema = Schema.build({"file_type": "columnar", "fields": []})
        rows = schema.parse(b"a")
        assert rows == [RowParsed(row_number=1, values={})]

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
        rows = schema.parse(b"1")
        assert rows == [RowParsed(row_number=1, values={"name": "1"})]

    def test_error_display_row_number(self):
        schema = Schema.build(
            {
                "file_type": "columnar",
                "fields": [
                    {"key": "age", "type": "int", "column-start": 0, "column-length": 1}
                ],
            }
        )
        rows = schema.parse(b"a")
        assert rows == [
            RowFailed(row_number=1, errors=[{
                "column-start": 0,
                "column-length": 1,
                "field-key": "age",
                "error": "value 'a' is not a valid integer",
            }])
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
        rows = schema.parse(b"1\na\n2")
        assert rows == [
            RowParsed(row_number=1, values={"age": 1}),
            RowFailed(row_number=2, errors=[{
                "column-start": 0,
                "column-length": 1,
                "field-key": "age",
                "error": "value 'a' is not a valid integer",
            }]),
            RowParsed(row_number=3, values={"age": 2}),
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
        rows = schema.parse(
            b"""8013109C

"""
        )
        assert rows == [RowParsed(row_number=1, values={"name": "8013109C"})]

    def test_should_return_all_errors_in_a_row(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "delimiter": ";",
                "fields": [
                    {"key": "age", "type": "int", "column-number": 1},
                    {"key": "age2", "type": "int", "column-number": 2}
                ],
            }
        )

        rows = schema.parse(b"a;a")

        assert rows == [
            RowFailed(row_number=1, errors=[
                {
                    "column-number": 1,
                    "field-key": "age",
                    "error": "value 'a' is not a valid integer",
                },
                {
                    "column-number": 2,
                    "field-key": "age2",
                    "error": "value 'a' is not a valid integer",
                }
            ])
        ]

    def test_skip_is_prioritized_over_errors(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "delimiter": ";",
                "fields": [
                    {
                        "key": "age",
                        "type": "int",
                        "column-number": 1,
                        "validators": [
                            {
                                "name": "greater-than",
                                "parameters": {"threshold": 0},
                                "on-error": "skip-row"
                            }
                        ],
                    },
                    {"key": "age2", "type": "int", "column-number": 2}
                ],
            }
        )

        rows = schema.parse(b"-1;a")

        assert rows == [
            RowSkipped(row_number=1, errors=[
                {
                    "column-number": 1,
                    "field-key": "age",
                    "error": "value must be greater than 0",
                },
                {
                    "column-number": 2,
                    "field-key": "age2",
                    "error": "value 'a' is not a valid integer",
                }
            ])
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
        rows = schema.parse(b"column_1\n6.66")
        assert rows == [
            RowParsed(row_number=2, values={"column_1": Decimal("6.66")})
        ]

    def test_single_quote(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "quotechar": "'",
                "has_header": True,
                "fields": [{"key": "column_1", "type": "decimal", "column-number": 1}],
            }
        )
        rows = schema.parse(b"column_1\n'6.66'")
        assert rows == [
            RowParsed(row_number=2, values={"column_1": Decimal("6.66")})
        ]

    def test_double_quote(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "quotechar": '"',
                "has_header": True,
                "fields": [{"key": "column_1", "type": "decimal", "column-number": 1}],
            }
        )
        rows = schema.parse(b'column_1\n"6.66"')
        assert rows == [
            RowParsed(row_number=2, values={"column_1": Decimal("6.66")})
        ]

    def test_asymetrical_quote(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "has_header": True,
                "fields": [{"key": "column_1", "type": "str", "column-number": 1}],
            }
        )
        rows = schema.parse(b'column_1\n"test ""quoting""')
        assert rows == [
            RowParsed(row_number=2, values={"column_1": '"test ""quoting""'})
        ]


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
            RowParsed(row_number=1, values={"age": 1}),
            RowFailed(
                row_number=2,
                errors=[
                    {
                        "column-number": 1,
                        "field-key": "age",
                        "error": "value 'a' is not a valid integer",
                    }
                ]),
            RowParsed(row_number=3, values={"age": 2}),
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


class TestComputedFields(TestCase):
    def test_concat(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "delimiter": ";",
                "fields": [
                    {"key": "field_1", "type": "str", "column-number": 1},
                    {"key": "field_2", "type": "str", "column-number": 2},
                ],
                "computed-fields": [
                    {
                        "key": "computed_field",
                        "type": "str",
                        "builder": {
                            "name": "concat",
                            "parameters": {
                                "fields": ["field_1", "field_2"],
                            },
                        },
                    }
                ],
            }
        )
        rows = list(schema.stream_parse(b"A;B"))
        print(rows)
        assert len(rows) == 1
        assert rows[0].row_number == 1
        assert rows[0].values == {
            "field_1": "A",
            "field_2": "B",
            "computed_field": "AB",
        }

    def test_computed_fields_can_be_used_by_next_computed_fields(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "delimiter": ";",
                "fields": [
                    {"key": "field_1", "type": "int", "column-number": 1},
                    {"key": "field_2", "type": "int", "column-number": 2},
                    {"key": "field_3", "type": "int", "column-number": 3},
                ],
                "computed-fields": [
                    {
                        "key": "multiply_field_result",
                        "type": "int",
                        "builder": {
                            "name": "multiply",
                            "parameters": {
                                "x_factor": "field_1",
                                "y_factor": "field_2",
                            },
                        },
                    },
                    {
                        "key": "divide_field_result",
                        "type": "decimal",
                        "builder": {
                            "name": "divide",
                            "parameters": {
                                "numerator": "multiply_field_result",
                                "denominator": "field_3",
                            },
                        },
                    }
                ],
            }
        )

        rows = list(schema.stream_parse(b"3;4;2"))

        assert rows == [
            RowParsed(
                row_number=1,
                values={
                    "field_1": 3,
                    "field_2": 4,
                    "field_3": 2,
                    "multiply_field_result": 12,
                    "divide_field_result": Decimal("6")
                }
            )
        ]


class TestHandleTypeError(TestCase):
    def test_default_behavior_raise(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [
                    {"key": "age", "type": "int", "column-number": 1}
                ],
            }
        )
        rows = list(schema.stream_parse(b"a"))
        assert rows == [
            RowFailed(row_number=1, errors=[{
                    "column-number": 1,
                    "field-key": "age",
                    "error": "value 'a' is not a valid integer",
                }])
        ]

    def test_skip_row(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [
                    {
                        "key": "age",
                        "type": {"key": "int", "on-error": "skip-row"},
                        "column-number": 1,
                    }
                ],
            }
        )
        rows = list(schema.stream_parse(b"a"))
        assert rows == [RowSkipped(row_number=1, errors=[{
                "column-number": 1,
                "field-key": "age",
                "error": "value 'a' is not a valid integer",
            }
        ])]


class TestHandleValidationError(TestCase):
    def test_default_behavior_raise(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [
                    {
                        "key": "age",
                        "type": "int",
                        "column-number": 1,
                        "validators": [
                            {
                                "name": "greater-than",
                                "parameters": {"threshold": 0},
                            }
                        ],
                    }
                ],
            }
        )

        rows = list(schema.stream_parse(b"-1"))

        assert rows == [
            RowFailed(row_number=1, errors=[{
                    "column-number": 1,
                    "field-key": "age",
                    "error": "value must be greater than 0",
                }
            ])
        ]

    def test_skip_row(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [
                    {
                        "key": "age",
                        "type": "int",
                        "column-number": 1,
                        "validators": [
                            {
                                "name": "greater-than",
                                "parameters": {"threshold": 0},
                                "on-error": "skip-row",
                            }
                        ],
                    }
                ],
            }
        )
        rows = list(schema.stream_parse(b"-1"))
        assert rows == [RowSkipped(row_number=1, errors=[{
                "column-number": 1,
                "field-key": "age",
                "error": "value must be greater than 0",
            }
        ])]


class TestHandlePostProcessorError(TestCase):
    class FailPostProcessor(PostProcessor):
        def apply(self, value: Any) -> Any:
            raise ValueError("test error")

        @staticmethod
        def key() -> str:
            return "fail-post-processor"

    def test_default_behavior_raise(self):
        PostProcessor.register(self.FailPostProcessor)
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [
                    {
                        "key": "age",
                        "type": "int",
                        "column-number": 1,
                        "post-processors": [
                            {
                                "name": "fail-post-processor",
                            }
                        ],
                    }
                ],
            }
        )
        rows = list(schema.stream_parse(b"1"))
        assert rows == [RowFailed(row_number=1, errors=[{
                    "column-number": 1,
                    "field-key": "age",
                    "error": "test error",
                }
            ])]

    def test_skip_row(self):
        PostProcessor.register(self.FailPostProcessor)
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [
                    {
                        "key": "age",
                        "type": "int",
                        "column-number": 1,
                        "post-processors": [
                            {
                                "name": "fail-post-processor",
                                "on-error": "skip-row",
                            }
                        ],
                    }
                ],
            }
        )
        rows = list(schema.stream_parse(b"1"))
        assert rows == [RowSkipped(row_number=1, errors=[{
                "column-number": 1,
                "field-key": "age",
                "error": "test error",
            }
        ])]


class TestHandlePreProcessorError(TestCase):
    class FailPreProcessor(PreProcessor):
        def apply(self, value: Any) -> Any:
            raise ValueError("test error")

        @staticmethod
        def key() -> str:
            return "fail-pre-processor"

    def test_default_behavior_raise(self):
        PreProcessor.register(self.FailPreProcessor)
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [
                    {
                        "key": "age",
                        "type": "int",
                        "column-number": 1,
                        "pre-processors": [
                            {
                                "name": "fail-pre-processor",
                            }
                        ],
                    }
                ],
            }
        )
        rows = list(schema.stream_parse(b"1"))
        assert rows == [RowFailed(row_number=1, errors=[{
                    "column-number": 1,
                    "field-key": "age",
                    "error": "test error",
                }
            ])]

    def test_skip_row(self):
        PreProcessor.register(self.FailPreProcessor)
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [
                    {
                        "key": "age",
                        "type": "int",
                        "column-number": 1,
                        "pre-processors": [
                            {
                                "name": "fail-pre-processor",
                                "on-error": "skip-row",
                            }
                        ],
                    }
                ],
            }
        )
        rows = list(schema.stream_parse(b"1"))
        assert rows == [RowSkipped(row_number=1, errors=[{
                "column-number": 1,
                "field-key": "age",
                "error": "test error",
            }
        ])]
