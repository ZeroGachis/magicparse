from decimal import Decimal
from magicparse import Transform
import pytest

from magicparse.transform import SkippedRow, TransformError


def test_assert_positive():
    assert Transform("$assert_positive(1)").evaluate({})

    with pytest.raises(TransformError, match="Value is not positive"):
        Transform("$assert_positive(0)").evaluate({})

    with pytest.raises(TransformError, match="Value is not positive"):
        Transform("$assert_positive(-1)").evaluate({})


def test_coalesce_numbers():
    assert Transform("$coalesce_numbers(1, 2, 3)").evaluate({}) == 1
    assert Transform("$coalesce_numbers(0, 2, 3)").evaluate({}) == 2
    assert Transform("$coalesce_numbers(0, 0, 3)").evaluate({}) == 3

    with pytest.raises(TransformError, match="No non-zero value to coalesce into"):
        Transform("$coalesce_numbers(0, 0, 0)").evaluate({})


def test_divide():
    assert Transform("$divide(1, 2)").evaluate({}) == 0.5

    assert Transform("$divide(a, b)").evaluate({"a": Decimal(1), "b": Decimal(2)}) == Decimal("0.5")

    with pytest.raises(TransformError, match="Cannot divide"):
        Transform("$divide(1, 0)").evaluate({})


def test_left_pad_zeroes():
    assert Transform('$left_pad_zeroes("", 5)').evaluate({}) == "00000"
    assert Transform('$left_pad_zeroes("111", 5)').evaluate({}) == "00111"
    assert Transform('$left_pad_zeroes("11111", 5)').evaluate({}) == "11111"
    assert Transform('$left_pad_zeroes("11111111", 5)').evaluate({}) == "11111111"

    with pytest.raises(TransformError, match="Cannot left pad zeroes"):
        Transform("$left_pad_zeroes(-1, 5)").evaluate({})


def test_length():
    assert Transform('$length(["A", "B", "C"])').evaluate({}) == 3
    assert Transform('$length("ABCD")').evaluate({}) == 4
    assert Transform("$length($)").evaluate({"a": "a", "b": "b"}) == 2

    with pytest.raises(TransformError, match="Cannot get length"):
        Transform("$length(5)").evaluate({})


def test_map_to():
    expression = """
    (
        $values := {
            "A": 1,
            "B": 2
        };
        input ~> $map_to($values)
    )
    """
    assert Transform(expression).evaluate({"input": "A"}) == 1
    assert Transform(expression).evaluate({"input": "B"}) == 2

    with pytest.raises(TransformError, match="Cannot map to"):
        Transform(expression).evaluate({"input": "C"})


def test_skip_row():
    with pytest.raises(SkippedRow, match="some reason"):
        Transform('$skip_row("some reason")').evaluate({})


def test_skip_row_if():
    Transform('$skip_row_if(1 > 2, "some reason")').evaluate({})

    with pytest.raises(SkippedRow, match="some reason"):
        Transform('$skip_row_if(2 > 1, "some reason")').evaluate({})


def test_strip_whitespaces():
    assert Transform('$strip_whitespaces("ABC")').evaluate({}) == "ABC"
    assert Transform('$strip_whitespaces("   ABC   ")').evaluate({}) == "ABC"

    with pytest.raises(TransformError, match="Cannot strip whitespaces"):
        Transform("$strip_whitespaces(5)").evaluate({})


def test_to_decimal():
    assert Transform("$to_decimal(1)").evaluate({}) == Decimal(1)
    assert Transform("$to_decimal(1.5)").evaluate({}) == Decimal("1.5")
    assert Transform('$to_decimal("1.5")').evaluate({}) == Decimal("1.5")
    assert Transform('$to_decimal("1,5")').evaluate({}) == Decimal("1.5")
    assert Transform('$to_decimal("  1.5   ")').evaluate({}) == Decimal("1.5")

    with pytest.raises(TransformError, match="Cannot convert to decimal"):
        Transform('$to_decimal("abc")').evaluate({})


def test_to_int():
    assert Transform('$to_int("15")').evaluate({}) == 15
    assert Transform('$to_int("    15  ")').evaluate({}) == 15

    with pytest.raises(TransformError, match="Cannot convert to int"):
        Transform('$to_int("abc")').evaluate({})


def test_type_of():
    assert Transform('$type_of("abc")').evaluate({}) == "string"
    assert Transform("$type_of(1)").evaluate({}) == "int"
    assert Transform("$type_of(1.5)").evaluate({}) == "float"
    assert Transform("$type_of(input)").evaluate({"input": Decimal("1.5")}) == "decimal"
    assert Transform("$type_of({})").evaluate({}) == "<class 'dict'>"
