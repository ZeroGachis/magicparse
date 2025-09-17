from decimal import Decimal

import pytest
from unittest import TestCase

from magicparse import Builder


class TestBuild(TestCase):
    class WithoutParamBuilder(Builder):
        @staticmethod
        def key() -> str:
            return "without-param"

        def transform(self, value):
            pass

    class WithParamBuilder(Builder):
        def __init__(self, on_error: str, setting: str) -> None:
            super().__init__(on_error)
            self.setting = setting

        @staticmethod
        def key() -> str:
            return "with-param"

        def transform(self, value):
            pass

    def test_without_parameter(self):
        Builder.register(self.WithoutParamBuilder)

        builder = Builder.build({"name": "without-param"})
        assert isinstance(builder, self.WithoutParamBuilder)

    def test_with_parameter(self):
        Builder.register(self.WithParamBuilder)

        builder = Builder.build(
            {"name": "with-param", "parameters": {"setting": "value"}}
        )
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
        builder = Builder.build(
            {"name": "concat", "parameters": {"fields": ["code_1", "code_2"]}}
        )
        with pytest.raises(KeyError):
            builder.transform({})

    def test_concat_two_fields(self):
        builder = Builder.build(
            {"name": "concat", "parameters": {"fields": ["code_1", "code_2"]}}
        )

        result = builder.transform({"code_1": "X", "code_2": "Y"})

        assert result == "XY"

    def test_concat_three_fields(self):
        builder = Builder.build(
            {"name": "concat", "parameters": {"fields": ["code_1", "code_2", "code_3"]}}
        )

        result = builder.transform({"code_1": "X", "code_2": "Y", "code_3": "Z"})

        assert result == "XYZ"

    def test_concat_integer(self):
        builder = Builder.build(
            {"name": "concat", "parameters": {"fields": ["code_1", "code_2"]}}
        )

        with pytest.raises(TypeError):
            builder.transform({"code_1": 1, "code_2": 2})


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
            builder.transform({})

    def test_numerator_not_valid(self):
        builder = Builder.build(
            {
                "name": "divide",
                "parameters": {"numerator": "price", "denominator": "price_by_unit"},
            }
        )
        with pytest.raises(TypeError):
            builder.transform({"price": "e", "price_by_unit": 1})

    def test_denominator_not_valid(self):
        builder = Builder.build(
            {
                "name": "divide",
                "parameters": {"numerator": "price", "denominator": "price_by_unit"},
            }
        )
        with pytest.raises(TypeError):
            builder.transform({"price": 1, "price_by_unit": "ee"})

    def test_valid_param(self):
        builder = Builder.build(
            {
                "name": "divide",
                "parameters": {"numerator": "price", "denominator": "price_by_unit"},
            }
        )

        result = builder.transform({"price": 1, "price_by_unit": 2})

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
            builder.transform({})

    def test_x_y_factor_not_valid(self):
        builder = Builder.build(
            {
                "name": "multiply",
                "parameters": {"x_factor": "price", "y_factor": "unit"},
            }
        )
        with pytest.raises(TypeError):
            builder.transform({"price": "e", "unit": "e"})

    def test_valid_param(self):
        builder = Builder.build(
            {
                "name": "multiply",
                "parameters": {"x_factor": "price", "y_factor": "unit"},
            }
        )

        result = builder.transform({"price": 1.5, "unit": 2})

        assert result == 3
