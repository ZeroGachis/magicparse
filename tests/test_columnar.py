from decimal import Decimal
from csvmagic import parse
from unittest import TestCase


class Test(TestCase):
    def test_parse_one_row(self):
        schema = {
            "file_type": "columnar",
            "fields": [
                {"key": "name", "type": "str", "column-start": 0, "column-length": 5},
            ],
        }
        rows, errors = parse("Bob  ", schema)
        assert not errors
        assert rows == [{"name": "Bob  "}]

    def test_parse_multiple_rows(self):
        schema = {
            "file_type": "columnar",
            "fields": [
                {"key": "name", "type": "str", "column-start": 0, "column-length": 5},
            ],
        }
        rows, errors = parse("Bob  \r\nJohn ", schema)
        assert not errors
        assert rows == [{"name": "Bob  "}, {"name": "John "}]

    def test_parse_multiple_fields(self):
        schema = {
            "file_type": "columnar",
            "fields": [
                {"key": "name", "type": "str", "column-start": 0, "column-length": 5},
                {"key": "age", "type": "int", "column-start": 5, "column-length": 2},
            ],
        }
        rows, errors = parse("Bob  42\r\nJohn  9", schema)
        assert not errors
        assert rows == [{"name": "Bob  ", "age": 42}, {"name": "John ", "age": 9}]


class TestPreProcessors(TestCase):
    def test_strip_modifer(self):
        schema = {
            "file_type": "columnar",
            "fields": [
                {
                    "key": "name",
                    "type": "str",
                    "column-start": 0,
                    "column-length": 5,
                    "pre-processors": [{"name": "strip-whitespaces"}],
                },
            ],
        }
        rows, errors = parse("Bob  ", schema)
        assert not errors
        assert rows == [{"name": "Bob"}]

    def test_left_pad_zeroes(self):
        schema = {
            "file_type": "columnar",
            "fields": [
                {
                    "key": "barcode",
                    "type": "str",
                    "column-start": 0,
                    "column-length": 3,
                    "pre-processors": [
                        {"name": "left-pad-zeroes", "parameters": {"width": 13}}
                    ],
                },
            ],
        }
        rows, errors = parse("123", schema)
        assert not errors
        assert rows == [{"barcode": "0000000000123"}]


class TestValidators(TestCase):
    def test_regex_matches_failure(self):
        schema = {
            "file_type": "columnar",
            "fields": [
                {
                    "key": "ean13",
                    "type": "str",
                    "column-start": 0,
                    "column-length": 13,
                    "validators": [
                        {
                            "name": "regex-matches",
                            "parameters": {"pattern": "^\\d{13}$"},
                        }
                    ],
                }
            ],
        }
        rows, errors = parse("123", schema)
        assert not rows
        assert errors == [
            {
                "column-length": 13,
                "column-start": 0,
                "error": "string does not match regex '^\\d{13}$'",
                "field-key": "ean13",
                "row-number": 1,
            }
        ]

    def test_regex_matches_success(self):
        schema = {
            "file_type": "columnar",
            "fields": [
                {
                    "key": "ean13",
                    "type": "str",
                    "column-start": 0,
                    "column-length": 13,
                    "validators": [
                        {
                            "name": "regex-matches",
                            "parameters": {"pattern": "^\\d{13}$"},
                        }
                    ],
                }
            ],
        }

        rows, errors = parse("0000000000042", schema)
        assert not errors
        assert rows == [{"ean13": "0000000000042"}]


class TestPostProcessors(TestCase):
    def test_divide(self):
        schema = {
            "file_type": "columnar",
            "fields": [
                {
                    "key": "vat",
                    "type": "decimal",
                    "column-start": 0,
                    "column-length": 4,
                    "post-processors": [
                        {"name": "divide", "parameters": {"denominator": 100}}
                    ],
                }
            ],
        }
        rows, errors = parse("65.3", schema)
        assert not errors
        assert rows == [{"vat": Decimal("0.653")}]
