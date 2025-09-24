from decimal import Decimal
from typing import Any

import pytest
from unittest import TestCase

from magicparse import Builder
from magicparse.transform import OnError


class TestBuild(TestCase):
    class WithoutParamBuilder(Builder):
        @staticmethod
        def key() -> str:
            return "without-param"

        def apply(self, value: Any):
            pass

    class WithParamBuilder(Builder):
        def __init__(self, on_error: OnError, setting: str) -> None:
            super().__init__(on_error)
            self.setting = setting

        @staticmethod
        def key() -> str:
            return "with-param"

        def apply(self, value: Any):
            pass

    def test_without_parameter(self):
        Builder.register(self.WithoutParamBuilder)

        builder = Builder.build({"name": "without-param"})
        assert isinstance(builder, self.WithoutParamBuilder)

    def test_with_parameter(self):
        Builder.register(self.WithParamBuilder)

        builder = Builder.build({"name": "with-param", "parameters": {"setting": "value"}})
        assert isinstance(builder, self.WithParamBuilder)
        assert builder.setting == "value"

    def test_unknown(self):
        with pytest.raises(ValueError, match="invalid builder 'anything'"):
            Builder.build({"name": "anything"})

    def test_no_name_provided(self):
        with pytest.raises(ValueError, match="builder must have a 'name' key"):
            Builder.build({})


class TestConcat(TestCase):
    def test_no_params(self):
        with pytest.raises(TypeError):
            Builder.build({"name": "concat"})

    def test_empty_params(self):
        with pytest.raises(TypeError):
            Builder.build({"name": "concat", "parameters": ""})

    def test_fields_params_empty(self):
        with pytest.raises(ValueError):
            Builder.build({"name": "concat", "parameters": {"fields": ""}})

    def test_fields_params_not_a_list_of_str(self):
        with pytest.raises(ValueError):
            Builder.build({"name": "concat", "parameters": {"fields": "xxx"}})

    def test_fields_params_has_less_than_two_field(self):
        with pytest.raises(ValueError):
            Builder.build({"name": "concat", "parameters": {"fields": ["code"]}})

    def test_field_not_present(self):
        builder = Builder.build({"name": "concat", "parameters": {"fields": ["code_1", "code_2"]}})
        with pytest.raises(KeyError):
            builder.apply({})

    def test_concat_two_fields(self):
        builder = Builder.build({"name": "concat", "parameters": {"fields": ["code_1", "code_2"]}})

        result = builder.apply({"code_1": "X", "code_2": "Y"})

        assert result == "XY"

    def test_concat_three_fields(self):
        builder = Builder.build({"name": "concat", "parameters": {"fields": ["code_1", "code_2", "code_3"]}})

        result = builder.apply({"code_1": "X", "code_2": "Y", "code_3": "Z"})

        assert result == "XYZ"

    def test_concat_integer(self):
        builder = Builder.build({"name": "concat", "parameters": {"fields": ["code_1", "code_2"]}})

        with pytest.raises(TypeError):
            builder.apply({"code_1": 1, "code_2": 2})


class TestDivide(TestCase):
    def test_no_params(self):
        with pytest.raises(TypeError):
            Builder.build({"name": "divide"})

    def test_empty_params(self):
        with pytest.raises(TypeError):
            Builder.build({"name": "divide", "parameters": ""})

    def test_numerator_param_empty(self):
        with pytest.raises(ValueError):
            Builder.build(
                {
                    "name": "divide",
                    "parameters": {"numerator": "", "denominator": "price_by_unit"},
                }
            )

    def test_denominator_param_empty(self):
        with pytest.raises(ValueError):
            Builder.build(
                {
                    "name": "divide",
                    "parameters": {"numerator": "price", "denominator": ""},
                }
            )

    def test_field_not_present(self):
        builder = Builder.build(
            {
                "name": "divide",
                "parameters": {"numerator": "price", "denominator": "price_by_unit"},
            }
        )
        with pytest.raises(KeyError):
            builder.apply({})

    def test_numerator_not_valid(self):
        builder = Builder.build(
            {
                "name": "divide",
                "parameters": {"numerator": "price", "denominator": "price_by_unit"},
            }
        )
        with pytest.raises(TypeError):
            builder.apply({"price": "e", "price_by_unit": 1})

    def test_denominator_not_valid(self):
        builder = Builder.build(
            {
                "name": "divide",
                "parameters": {"numerator": "price", "denominator": "price_by_unit"},
            }
        )
        with pytest.raises(TypeError):
            builder.apply({"price": 1, "price_by_unit": "ee"})

    def test_valid_param(self):
        builder = Builder.build(
            {
                "name": "divide",
                "parameters": {"numerator": "price", "denominator": "price_by_unit"},
            }
        )

        result = builder.apply({"price": 1, "price_by_unit": 2})

        assert result == Decimal("0.5")


class TestMultiply(TestCase):
    def test_no_params(self):
        with pytest.raises(TypeError):
            Builder.build({"name": "multiply"})

    def test_empty_params(self):
        with pytest.raises(TypeError):
            Builder.build({"name": "multiply", "parameters": ""})

    def test_x_factor_param_empty(self):
        with pytest.raises(ValueError):
            Builder.build(
                {
                    "name": "multiply",
                    "parameters": {"x_factor": "", "y_factor": "unit"},
                }
            )

    def test_y_factor_param_empty(self):
        with pytest.raises(ValueError):
            Builder.build(
                {
                    "name": "multiply",
                    "parameters": {"x_factor": "price", "y_factor": ""},
                }
            )

    def test_field_not_present(self):
        builder = Builder.build(
            {
                "name": "multiply",
                "parameters": {"x_factor": "price", "y_factor": "unit"},
            }
        )
        with pytest.raises(KeyError):
            builder.apply({})

    def test_x_y_factor_not_valid(self):
        builder = Builder.build(
            {
                "name": "multiply",
                "parameters": {"x_factor": "price", "y_factor": "unit"},
            }
        )
        with pytest.raises(TypeError):
            builder.apply({"price": "e", "unit": "e"})

    def test_valid_param(self):
        builder = Builder.build(
            {
                "name": "multiply",
                "parameters": {"x_factor": "price", "y_factor": "unit"},
            }
        )

        result = builder.apply({"price": 1.5, "unit": 2})

        assert result == 3


class TestCoalesce(TestCase):
    def test_no_params(self):
        with pytest.raises(TypeError):
            Builder.build({"name": "coalesce"})

    def test_empty_params(self):
        with pytest.raises(TypeError):
            Builder.build({"name": "coalesce", "parameters": ""})

    def test_fields_params_empty(self):
        with pytest.raises(ValueError, match="parameters should defined fields to coalesce"):
            Builder.build({"name": "coalesce", "parameters": {"fields": ""}})

    def test_fields_params_not_a_list_of_str(self):
        with pytest.raises(ValueError, match="parameters should have two fields at least"):
            Builder.build({"name": "coalesce", "parameters": {"fields": "xxx"}})

    def test_fields_params_has_less_than_two_fields(self):
        with pytest.raises(ValueError, match="parameters should have two fields at least"):
            Builder.build({"name": "coalesce", "parameters": {"fields": ["field"]}})

    def test_return_first_non_empty_value(self):
        coalesce = Builder.build({"name": "coalesce", "parameters": {"fields": ["field1", "field2"]}})

        result = coalesce.apply({"field1": "", "field2": "value"})

        assert result == "value"

    def test_return_none_if_all_values_are_empty(self):
        coalesce = Builder.build({"name": "coalesce", "parameters": {"fields": ["field1", "field2"]}})

        result = coalesce.apply({"field1": "", "field2": ""})

        assert result is None
