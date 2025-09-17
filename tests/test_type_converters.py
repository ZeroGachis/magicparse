from datetime import datetime, time, timedelta, timezone
from decimal import Decimal
from unittest import TestCase
from uuid import UUID

import pytest

from magicparse.type_converters import (
    DateTimeConverter,
    DecimalConverter,
    IntConverter,
    StrConverter,
    TimeConverter,
    TypeConverter,
)


class TestBuildFlattenType(TestCase):
    def test_str(self):
        type_converter = TypeConverter.build({"type": "str"})
        assert isinstance(type_converter, StrConverter)

    def test_int(self):
        type_converter = TypeConverter.build({"type": "int"})
        assert isinstance(type_converter, IntConverter)

    def test_decimal(self):
        type_converter = TypeConverter.build({"type": "decimal"})
        assert isinstance(type_converter, DecimalConverter)

    def test_time(self):
        type_converter = TypeConverter.build({"type": "time"})
        assert isinstance(type_converter, TimeConverter)

    def test_datetime(self):
        type_converter = TypeConverter.build({"type": "datetime"})
        assert isinstance(type_converter, DateTimeConverter)

    def test_unknown(self):
        with pytest.raises(ValueError, match="invalid type 'anything'"):
            TypeConverter.build({"type": "anything"})

    def test_no_type_provided(self):
        with pytest.raises(ValueError, match="missing key 'type'"):
            TypeConverter.build({})

class TestBuildComplexeType(TestCase):
    def test_str(self):
        type_converter = TypeConverter.build({"type": {"key": "str"}})
        assert isinstance(type_converter, StrConverter)

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

        with pytest.raises(ValueError, match="value 'abc' is not a valid integer"):
            type_converter.apply("abc")


class TestDecimal(TestCase):
    def test_apply(self):
        type_converter = TypeConverter.build({"type": "decimal"})
        assert type_converter.apply("153.56") == Decimal("153.56")

    def test_apply_failed(self):
        type_converter = TypeConverter.build({"type": "decimal"})

        with pytest.raises(ValueError, match="value 'abc' is not a valid decimal"):
            type_converter.apply("abc")


class TestTime(TestCase):
    def test_apply(self):
        type_converter = TypeConverter.build({"type": "time"})
        assert type_converter.apply("10:12:03+03:00") == time(
            10, 12, 3, tzinfo=timezone(timedelta(hours=3))
        )

    def test_apply_failed(self):
        type_converter = TypeConverter.build({"type": "time"})

        with pytest.raises(ValueError):
            type_converter.apply("Invalid")

    def test_apply_naive_time(self):
        type_converter = TypeConverter.build({"type": "time"})

        with pytest.raises(ValueError):
            type_converter.apply("10:12:03")


class TestDateTime(TestCase):
    def test_apply(self):
        type_converter = TypeConverter.build({"type": "datetime"})
        assert type_converter.apply("2022-01-12T10:12:03+03:00") == datetime(
            2022, 1, 12, 10, 12, 3, tzinfo=timezone(timedelta(hours=3))
        )

    def test_apply_failed(self):
        type_converter = TypeConverter.build({"type": "datetime"})

        with pytest.raises(ValueError):
            type_converter.apply("Invalid")

    def test_apply_naive_time(self):
        type_converter = TypeConverter.build({"type": "datetime"})

        with pytest.raises(ValueError):
            type_converter.apply("2022-01-12T10:12:03")


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
