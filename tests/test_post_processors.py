from decimal import Decimal
from magicparse.post_processors import Divide, PostProcessor
import pytest
from unittest import TestCase


class TestBuild(TestCase):
    def test_divide(self):
        pre_processor = PostProcessor.build(
            {"name": "divide", "parameters": {"denominator": 100}}
        )
        assert isinstance(pre_processor, Divide)
        assert pre_processor.denominator == 100

    def test_unknown(self):
        with pytest.raises(ValueError, match="invalid post-processor 'anything'"):
            PostProcessor.build({"name": "anything"})

    def test_no_name_provided(self):
        with pytest.raises(ValueError, match="post-processor must have a 'name' key"):
            PostProcessor.build({})


class TestDivide(TestCase):
    def test_fail_when_denominator_is_zero(self):
        error_message = (
            "post-processor 'divide': "
            "'denominator' parameter must be a positive integer"
        )
        with pytest.raises(ValueError, match=error_message):
            PostProcessor.build({"name": "divide", "parameters": {"denominator": 0}})

    def test_divide_int(self):
        post_processor = PostProcessor.build(
            {"name": "divide", "parameters": {"denominator": 100}}
        )
        assert post_processor.apply(150) == 1.5

    def test_divide_float(self):
        post_processor = PostProcessor.build(
            {"name": "divide", "parameters": {"denominator": 100}}
        )
        assert post_processor.apply(1.63) == 0.0163

    def test_divide_decimal(self):
        post_processor = PostProcessor.build(
            {"name": "divide", "parameters": {"denominator": 100}}
        )
        assert post_processor.apply(Decimal("1.63")) == Decimal("0.0163")


class TestRound(TestCase):
    def test_with_negative_precision(self):
        error_message = (
            "post-processor 'round': "
            "'precision' parameter must be a positive or zero integer"
        )
        with pytest.raises(ValueError, match=error_message):
            PostProcessor.build({"name": "round", "parameters": {"precision": -2}})

    def test_with_valid_precision(self):
        post_processor = PostProcessor.build(
            {"name": "round", "parameters": {"precision": 2}}
        )
        assert post_processor.apply(3.14159265359) == 3.14


class TestRegister(TestCase):
    class NoThanksPostProcessor(PostProcessor):
        @staticmethod
        def key() -> str:
            return "no-thanks"

        def apply(self, value):
            return f"{value} ? No thanks"

    def test_register(self):
        PostProcessor.register(self.NoThanksPostProcessor)

        post_processor = PostProcessor.build({"name": "no-thanks"})
        assert isinstance(post_processor, self.NoThanksPostProcessor)
