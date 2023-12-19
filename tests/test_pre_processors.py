import re
from magicparse.pre_processors import (
    LeftPadZeroes,
    Map,
    PreProcessor,
    RegexExtract,
    Replace,
    StripWhitespaces,
    LeftStrip,
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

    def test_left_strip(self):
        pre_processor = PreProcessor.build(
            {"name": "left-strip", "parameters": {"characters": "0"}}
        )
        assert isinstance(pre_processor, LeftStrip)

    def test_regex_extract(self):
        pre_processor = PreProcessor.build(
            {
                "name": "regex-extract",
                "parameters": {"pattern": "^xxx(?P<value>\\d{13})xxx$"},
            }
        )
        assert isinstance(pre_processor, RegexExtract)
        assert isinstance(pre_processor.pattern, re.Pattern)
        assert pre_processor.pattern.pattern == "^xxx(?P<value>\\d{13})xxx$"

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

    def test_pad_with_regex(self):
        pre_processor = PreProcessor.build(
            {
                "name": "left-pad-zeroes", 
                "parameters": {"width": 10, "regex": "[a-z]{7}"},
            }
        )
        assert pre_processor.apply("abc") == "abc"
        assert pre_processor.apply("abcdefg") == "000abcdefg"


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


class TestLeftStrip(TestCase):
    def test_do_nothing(self):
        pre_processor = PreProcessor.build(
            {"name": "left-strip", "parameters": {"characters": "0"}}
        )
        assert pre_processor.apply("12345") == "12345"

    def test_success(self):
        pre_processor = PreProcessor.build(
            {"name": "left-strip", "parameters": {"characters": "0"}}
        )
        assert pre_processor.apply("0000012345") == "12345"


class TestRegexExtract(TestCase):
    def test_build_without_value_group(self):
        with pytest.raises(
            ValueError,
            match=r"regex-extract's pattern must contain a group named 'value'",
        ):
            PreProcessor.build(
                {"name": "regex-extract", "parameters": {"pattern": "xxx"}}
            )

    def test_pattern_not_found(self):
        pre_processor = PreProcessor.build(
            {
                "name": "regex-extract",
                "parameters": {"pattern": "^xxx(?P<value>\\d{13})xxx$"},
            }
        )
        with pytest.raises(ValueError) as error:
            pre_processor.apply("an input")

        assert (
            error.value.args[0]
            == "cannot extract value from pattern '^xxx(?P<value>\\d{13})xxx$'"
        )

    def test_pattern_found(self):
        pre_processor = PreProcessor.build(
            {
                "name": "regex-extract",
                "parameters": {"pattern": "^xxx(?P<value>\\d{13})xxx$"},
            }
        )
        pre_processor.apply("xxx9780201379624xxx") == "9780201379624"


class TestRegister(TestCase):
    class YesPreProcessor(PreProcessor):
        @staticmethod
        def key() -> str:
            return "yes"

        def apply(self, value):
            return f"YES {value}"

    def test_register(self):
        PreProcessor.register(self.YesPreProcessor)

        pre_processor = PreProcessor.build({"name": "yes"})
        assert isinstance(pre_processor, self.YesPreProcessor)
