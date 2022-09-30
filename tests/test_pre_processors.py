from csvmagic.pre_processors import (
    LeftPadZeroes,
    Map,
    PreProcessor,
    Replace,
    StripWhitespaces,
)
import pytest
from unittest import TestCase


class TestBuild(TestCase):
    def test_left_pad_zeroes(self):
        pre_processor = PreProcessor.build(
            {"name": "left-pad-zeroes", "parameters": {"width": 10}}
        )
        assert isinstance(pre_processor, LeftPadZeroes)
        assert pre_processor.width == 10

    def test_map(self):
        pre_processor = PreProcessor.build(
            {"name": "map", "parameters": {"values": {"input": "output"}}}
        )
        assert isinstance(pre_processor, Map)
        assert pre_processor.values == {"input": "output"}

    def test_replace(self):
        pre_processor = PreProcessor.build(
            {"name": "replace", "parameters": {"pattern": "aa", "replacement": "bb"}}
        )
        assert isinstance(pre_processor, Replace)
        assert pre_processor.pattern == "aa"
        assert pre_processor.replacement == "bb"

    def test_strip_whitespaces(self):
        pre_processor = PreProcessor.build({"name": "strip-whitespaces"})
        assert isinstance(pre_processor, StripWhitespaces)

    def test_unknown(self):
        with pytest.raises(ValueError, match="invalid pre-processor 'anything'"):
            PreProcessor.build({"name": "anything"})

    def test_no_name_provided(self):
        with pytest.raises(ValueError, match="pre-processor must have a 'name' key"):
            PreProcessor.build({})


class TestLeftPadZeroes(TestCase):
    def test_do_nothing(self):
        pre_processor = PreProcessor.build(
            {"name": "left-pad-zeroes", "parameters": {"width": 10}}
        )
        assert pre_processor.apply("abcdefghij") == "abcdefghij"

    def test_pad(self):
        pre_processor = PreProcessor.build(
            {"name": "left-pad-zeroes", "parameters": {"width": 10}}
        )
        assert pre_processor.apply("abc") == "0000000abc"


class TestMap(TestCase):
    def test_unknown_input(self):
        pre_processor = PreProcessor.build(
            {"name": "map", "parameters": {"values": {"A": "1", "B": "2"}}}
        )
        with pytest.raises(
            ValueError,
            match="value 'an input' does not map to any values in \\['A', 'B'\\]",
        ):
            pre_processor.apply("an input")

    def test_known_input(self):
        pre_processor = PreProcessor.build(
            {"name": "map", "parameters": {"values": {"A": "1", "B": "2"}}}
        )
        assert pre_processor.apply("A") == "1"


class TestReplace(TestCase):
    def test_pattern_not_found(self):
        pre_processor = PreProcessor.build(
            {"name": "replace", "parameters": {"pattern": "bbb", "replacement": "BBB"}}
        )
        assert pre_processor.apply("an input") == "an input"

    def test_success(self):
        pre_processor = PreProcessor.build(
            {"name": "replace", "parameters": {"pattern": "bbb", "replacement": "BBB"}}
        )
        assert pre_processor.apply("aaabbbccc") == "aaaBBBccc"


class TestStripWhitespaces(TestCase):
    def test_do_nothing(self):
        pre_processor = PreProcessor.build({"name": "strip-whitespaces"})
        assert pre_processor.apply("an input") == "an input"

    def test_success(self):
        pre_processor = PreProcessor.build({"name": "strip-whitespaces"})
        assert pre_processor.apply("    an input     ") == "an input"
