from magicparse.converters import Converter, DecimalConverter, IntConverter, StrConverter
from decimal import Decimal
import pytest
from unittest import TestCase


class TestBuild(TestCase):
    def test_str(self):
        converter = Converter.build({"type": "str"})
        assert isinstance(converter, StrConverter)

    def test_int(self):
        converter = Converter.build({"type": "int"})
        assert isinstance(converter, IntConverter)

    def test_decimal(self):
        converter = Converter.build({"type": "decimal"})
        assert isinstance(converter, DecimalConverter)

    def test_unknown(self):
        with pytest.raises(ValueError, match="invalid type 'anything'"):
            Converter.build({"type": "anything"})

    def test_no_type_provided(self):
        with pytest.raises(ValueError, match="missing key 'type'"):
            Converter.build({})


class TestStr(TestCase):
    def test_apply(self):
        converter = Converter.build({"type": "str"})
        assert converter.apply("hello") == "hello"


class TestInt(TestCase):
    def test_apply(self):
        converter = Converter.build({"type": "int"})
        assert converter.apply("153") == 153

    def test_apply_failed(self):
        converter = Converter.build({"type": "int"})

        with pytest.raises(ValueError, match="value is not a valid integer"):
            converter.apply("abc")


class TestDecimal(TestCase):
    def test_apply(self):
        converter = Converter.build({"type": "decimal"})
        assert converter.apply("153.56") == Decimal("153.56")

    def test_apply_failed(self):
        converter = Converter.build({"type": "decimal"})

        with pytest.raises(ValueError, match="value is not a valid decimal"):
            converter.apply("abc")
