from decimal import Decimal
from magicparse.validators import GreaterThan, NotNullOrEmpty, RegexMatches, Validator
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

    def test_not_null_or_empty(self):
        validator = Validator.build(
            {"name": "not-null-or-empty"}
        )

        assert isinstance(validator, NotNullOrEmpty)

    def test_unknown(self):
        with pytest.raises(ValueError, match="invalid validator 'anything'"):
            Validator.build({"name": "anything"})

    def test_no_name_provided(self):
        with pytest.raises(ValueError, match="validator must have a 'name' key"):
            Validator.build({})

    def test_greater_than_params_are_correct(self):
        validator = Validator.build(
            {
                "name": "greater-than",
                "parameters": {"threshold": 20.2},
            }
        )
        assert isinstance(validator, GreaterThan)
        assert isinstance(validator.threshold, Decimal)
        assert validator.threshold == 20.2


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


class TestGreaterThanValidator(TestCase):
    def test_it_successfully_returns_the_value_when_greater_than_threshold(self):
        validator = Validator.build(
            {"name": "greater-than", "parameters": {"threshold": 11}}
        )

        assert validator.apply(12) == 12

    def test_it_successfully_returns_the_value_when_greater_than_decimal_threshold(
        self,
    ):
        validator = Validator.build(
            {"name": "greater-than", "parameters": {"threshold": 11.4}}
        )

        assert validator.apply(11.5) == 11.5

    def test_it_raises_an_error_when_the_value_is_lower_than_threshold(self):
        validator = Validator.build(
            {"name": "greater-than", "parameters": {"threshold": 10}}
        )

        with pytest.raises(ValueError, match="value must be greater than 10"):
            validator.apply(9.9999)

    def test_it_raises_an_error_when_the_value_is_equal_to_threshold(self):
        validator = Validator.build(
            {"name": "greater-than", "parameters": {"threshold": 10}}
        )

        with pytest.raises(ValueError, match="value must be greater than 10"):
            validator.apply(10)


class TestNotNullOrEmptyValidator(TestCase):
    def test_success_returns_the_value(self):
        validator = Validator.build(
            {"name": "not-null-or-empty"}
        )

        assert validator.apply("hello") == "hello"

    def test_raise_when_the_value_is_null(self):
        validator = Validator.build(
            {"name": "not-null-or-empty"}
        )

        with pytest.raises(ValueError, match="value must not be null or empty"):
            validator.apply(None)

    def test_raises_when_the_value_is_empty(self):
        validator = Validator.build(
            {"name": "not-null-or-empty"}
        )

        with pytest.raises(ValueError, match="value must not be null or empty"):
            validator.apply("")
