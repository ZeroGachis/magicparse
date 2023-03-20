from decimal import Decimal
from magicparse.validators import LessThan, RegexMatches, Validator
import pytest
import re
from unittest import TestCase


class TestBuild(TestCase):
    def test_regex_matches(self):
        validator = Validator.build(
            {
                "name": "regex-matches",
                "parameters": {"pattern": "^\\d{13}$"},
            }
        )
        assert isinstance(validator, RegexMatches)
        assert isinstance(validator.pattern, re.Pattern)
        assert validator.pattern.pattern == "^\\d{13}$"

    def test_unknown(self):
        with pytest.raises(ValueError, match="invalid validator 'anything'"):
            Validator.build({"name": "anything"})

    def test_no_name_provided(self):
        with pytest.raises(ValueError, match="validator must have a 'name' key"):
            Validator.build({})

    def test_less_than(self):
        validator = Validator.build(
            {
                "name": "less-than",
                "parameters": {"threshold": "30.1"},
            }
        )
        assert isinstance(validator, LessThan)
        assert isinstance(validator.threshold, Decimal)
        assert validator.threshold == Decimal("30.1")


class TestRegexMatches(TestCase):
    def test_match(self):
        validator = Validator.build(
            {
                "name": "regex-matches",
                "parameters": {"pattern": "^\\d{13}$"},
            }
        )

        assert validator.apply("9780201379624") == "9780201379624"

    def test_does_not_match(self):
        validator = Validator.build(
            {
                "name": "regex-matches",
                "parameters": {"pattern": "^\\d{13}$"},
            }
        )
        with pytest.raises(
            ValueError, match=r"string does not match regex '\^\\d\{13\}\$'"
        ):
            validator.apply("hello")


class TestRegister(TestCase):
    class IsTheAnswerValidator(Validator):
        @staticmethod
        def key() -> str:
            return "is-the-answer"

        def apply(self, value):
            if value == 42:
                return value
            raise ValueError(f"{value} is not the answer !")

    def test_register(self):
        Validator.register(self.IsTheAnswerValidator)

        validator = Validator.build({"name": "is-the-answer"})
        assert isinstance(validator, self.IsTheAnswerValidator)


class TestLessThan(TestCase):
    def test_is_below_threshold(self):
        validator = Validator.build(
            {"name": "less-than", "parameters": {"threshold": "10"}}
        )

        assert validator.apply(Decimal("9.99999")) == Decimal("9.99999")

    def test_is_above_threshold(self):
        validator = Validator.build(
            {"name": "less-than", "parameters": {"threshold": "10"}}
        )

        with pytest.raises(ValueError, match=r"value is not less than 10"):
            validator.apply(Decimal("12"))

    def test_is_equal_to_threshold(self):
        validator = Validator.build(
            {"name": "less-than", "parameters": {"threshold": "10"}}
        )

        with pytest.raises(ValueError, match=r"value is not less than 10"):
            validator.apply(Decimal("10"))
