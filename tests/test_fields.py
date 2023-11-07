from decimal import Decimal

import pytest
from magicparse.type_converters import DecimalConverter, StrConverter
from magicparse.fields import ColumnarField, CsvField, Field
from magicparse.post_processors import Divide
from magicparse.pre_processors import Replace, StripWhitespaces
from magicparse.validators import RegexMatches


class DummyField(Field):
    def _read_raw_value(self, row: str) -> str:
        return row

    def error(self, exception: Exception):
        return {}


def test_chain_transformations():
    field = DummyField(
        {
            "key": "name",
            "type": "str",
            "pre-processors": [{"name": "strip-whitespaces"}],
            "validators": [
                {"name": "regex-matches", "parameters": {"pattern": "^mac .*$"}}
            ],
        }
    )
    assert len(field.transforms) == 3
    assert isinstance(field.transforms[0], StripWhitespaces)
    assert isinstance(field.transforms[1], StrConverter)
    assert isinstance(field.transforms[2], RegexMatches)

    result = field.read_value("   mac adam    ")
    assert result == "mac adam"


def test_chain_transformations_with_post_processors():
    # NB: Currently their is no valid combination that includes all
    # the 4 transformations at once.
    field = DummyField(
        {
            "key": "ratio",
            "type": "decimal",
            "pre-processors": [
                {
                    "name": "replace",
                    "parameters": {"pattern": "XXX", "replacement": "000"},
                }
            ],
            "post-processors": [{"name": "divide", "parameters": {"denominator": 100}}],
        }
    )
    assert len(field.transforms) == 3
    assert isinstance(field.transforms[0], Replace)
    assert isinstance(field.transforms[1], DecimalConverter)
    assert isinstance(field.transforms[2], Divide)
    assert field.read_value("XXX150") == Decimal("1.50")


def test_csv_error_format():
    field = CsvField({"key": "ratio", "type": "decimal", "column-number": 1})

    with pytest.raises(ValueError) as error:
        field.read_value("hello")

    assert field.error(error.value) == {
        "column-number": 1,
        "error": "value 'h' is not a valid decimal",
        "field-key": "ratio",
    }


def test_columnar_error_format():
    field = ColumnarField(
        {"key": "ratio", "type": "decimal", "column-start": 0, "column-length": 5}
    )

    with pytest.raises(ValueError) as error:
        field.read_value("hello")

    assert field.error(error.value) == {
        "column-start": 0,
        "column-length": 5,
        "error": "value 'hello' is not a valid decimal",
        "field-key": "ratio",
    }
