from decimal import Decimal
from csvmagic import parse
from unittest import TestCase


class TestWithHeader(TestCase):

    schema = {
        "file_type": "csv",
        "has_header": True,
        "delimiter": ",",
        "fields": [
            {"key": "name", "type": "str", "column-number": 1},
            {"key": "age", "type": "int", "column-number": 2},
        ],
    }

    def test_parse_one_row(self):
        rows, errors = parse("name,age\r\nJo,10", self.schema)
        assert not errors
        assert rows == [{"name": "Jo", "age": 10}]

    def test_parse_multiple_rows(self):
        rows, errors = parse("name,age\r\nJo,10\r\nMarcel,69\r\nBob,42", self.schema)
        assert not errors
        assert rows == [
            {"name": "Jo", "age": 10},
            {"name": "Marcel", "age": 69},
            {"name": "Bob", "age": 42},
        ]


class TestWithoutHeader(TestCase):
    schema = {
        "file_type": "csv",
        "has_header": False,
        "delimiter": ",",
        "fields": [
            {"key": "name", "type": "str", "column-number": 1},
            {"key": "age", "type": "int", "column-number": 2},
        ],
    }

    def test_parse_one_row(self):
        rows, errors = parse("Jo,10", self.schema)
        assert not errors
        assert rows == [{"name": "Jo", "age": 10}]

    def test_parse_multiple_rows(self):
        rows, errors = parse("Jo,10\r\nMarcel,69\r\nBob,42", self.schema)
        assert not errors
        assert rows == [
            {"name": "Jo", "age": 10},
            {"name": "Marcel", "age": 69},
            {"name": "Bob", "age": 42},
        ]


class TestPreProcessors(TestCase):
    def test_strip_modifer(self):
        schema = {
            "file_type": "csv",
            "has_header": False,
            "delimiter": ",",
            "fields": [
                {
                    "key": "name",
                    "type": "str",
                    "column-number": 1,
                    "pre-processors": [{"name": "strip-whitespaces"}],
                }
            ],
        }
        rows, errors = parse("  Bob  ", schema)
        assert not errors
        assert rows == [{"name": "Bob"}]

    def test_left_pad_zeroes(self):
        schema = {
            "file_type": "csv",
            "has_header": False,
            "delimiter": ",",
            "fields": [
                {
                    "key": "barcode",
                    "type": "str",
                    "column-number": 1,
                    "pre-processors": [
                        {"name": "left-pad-zeroes", "parameters": {"width": 13}}
                    ],
                }
            ],
        }

        rows, errors = parse("123", schema)
        assert not errors
        assert rows == [{"barcode": "0000000000123"}]

    def test_map(self):
        schema = {
            "file_type": "csv",
            "has_header": False,
            "delimiter": ",",
            "fields": [
                {
                    "key": "size",
                    "type": "str",
                    "column-number": 1,
                    "pre-processors": [
                        {
                            "name": "map",
                            "parameters": {
                                "values": {"S": "Small", "M": "Middle", "L": "Large"}
                            },
                        }
                    ],
                }
            ],
        }

        rows, errors = parse("S\r\nM\r\nL", schema)
        assert not errors
        assert rows == [{"size": "Small"}, {"size": "Middle"}, {"size": "Large"}]

    def test_replace(self):
        schema = {
            "file_type": "csv",
            "has_header": False,
            "delimiter": ";",
            "fields": [
                {
                    "key": "price",
                    "type": "decimal",
                    "column-number": 1,
                    "pre-processors": [
                        {
                            "name": "replace",
                            "parameters": {"pattern": ",", "replacement": "."},
                        }
                    ],
                }
            ],
        }

        rows, errors = parse("62,5", schema)
        assert not errors
        assert rows == [{"price": Decimal("62.5")}]


class TestValidators(TestCase):
    def test_regex_matches_failure(self):
        schema = {
            "file_type": "csv",
            "has_header": False,
            "delimiter": ",",
            "fields": [
                {
                    "key": "ean13",
                    "type": "str",
                    "column-number": 1,
                    "validators": [
                        {
                            "name": "regex-matches",
                            "parameters": {"pattern": "^\\d{13}$"},
                        }
                    ],
                }
            ],
        }
        rows, errors = parse("35", schema)
        assert not rows
        assert errors == [
            {
                "column-number": 1,
                "error": "string does not match regex '^\\d{13}$'",
                "field-key": "ean13",
                "row-number": 1,
            }
        ]

    def test_regex_matches_success(self):
        schema = {
            "file_type": "csv",
            "has_header": False,
            "delimiter": ",",
            "fields": [
                {
                    "key": "ean13",
                    "type": "str",
                    "column-number": 1,
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
            "file_type": "csv",
            "has_header": False,
            "delimiter": ",",
            "fields": [
                {
                    "key": "vat",
                    "type": "decimal",
                    "column-number": 1,
                    "post-processors": [
                        {"name": "divide", "parameters": {"denominator": 100}}
                    ],
                }
            ],
        }
        rows, errors = parse("65.3", schema)
        assert not errors
        assert rows == [{"vat": Decimal("0.653")}]
