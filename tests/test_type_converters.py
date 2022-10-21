from uuid import UUID
from magicparse.type_converters import (
    TypeConverter,
    DecimalConverter,
    IntConverter,
    StrConverter,
)
from decimal import Decimal
import pytest
from unittest import TestCase


class TestBuild(TestCase):
    def test_str(self):
        type_converter = TypeConverter.build({"type": "str"})
        assert isinstance(type_converter, StrConverter)

    def test_int(self):
        type_converter = TypeConverter.build({"type": "int"})
        assert isinstance(type_converter, IntConverter)

    def test_decimal(self):
        type_converter = TypeConverter.build({"type": "decimal"})
        assert isinstance(type_converter, DecimalConverter)

    def test_unknown(self):
        with pytest.raises(ValueError, match="invalid type 'anything'"):
            TypeConverter.build({"type": "anything"})

    def test_no_type_provided(self):
        with pytest.raises(ValueError, match="missing key 'type'"):
            TypeConverter.build({})


class TestStr(TestCase):
    def test_apply(self):
        type_converter = TypeConverter.build({"type": "str"})
        assert type_converter.apply("hello") == "hello"


class TestInt(TestCase):
    def test_apply(self):
        type_converter = TypeConverter.build({"type": "int"})
        assert type_converter.apply("153") == 153

    def test_apply_failed(self):
        type_converter = TypeConverter.build({"type": "int"})

        with pytest.raises(ValueError, match="value is not a valid integer"):
            type_converter.apply("abc")


class TestDecimal(TestCase):
    def test_apply(self):
        type_converter = TypeConverter.build({"type": "decimal"})
        assert type_converter.apply("153.56") == Decimal("153.56")

    def test_apply_failed(self):
        type_converter = TypeConverter.build({"type": "decimal"})

        with pytest.raises(ValueError, match="value is not a valid decimal"):
            type_converter.apply("abc")


class TestRegister(TestCase):
    class GuidConverter(TypeConverter):
        @staticmethod
        def key() -> str:
            return "guid"

        def apply(self, value):
            return UUID(value)

    def test_register(self):
        TypeConverter.register(self.GuidConverter)

        type_converter = TypeConverter.build({"type": "guid"})
        assert isinstance(type_converter, self.GuidConverter)
