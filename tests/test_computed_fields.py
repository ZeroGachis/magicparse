import pytest

from magicparse.fields import ComputedField
from unittest import TestCase

from magicparse.transform import Ok


class TestBuild(TestCase):
    def test_without_builder(self):
        with pytest.raises(KeyError):
            ComputedField("output", {"type": "str"})

    def test_not_iterable_value_for_builder(self):
        with pytest.raises(ValueError):
            ComputedField("output", {"type": "str", "builder": 1})

    def test_bad_value_for_builder(self):
        with pytest.raises(ValueError):
            ComputedField("output", {"type": "str", "builder": "really"})

    def test_with_valid_builder(self):
        field = ComputedField(
            "output",
            {
                "key": "output",
                "type": "str",
                "builder": {
                    "name": "concat",
                    "parameters": {"fields": ["code_1", "code_2"]},
                },
            }
        )

        computed = field.parse({"code_1": "01", "code_2": "02"})

        assert computed == Ok(value="0102")

    def test_error_format(self):
        field = ComputedField(
            "output",
            {
                "key": "output",
                "type": "str",
                "builder": {
                    "name": "concat",
                    "parameters": {"fields": ["code_1", "code_2"]},
                },
            }
        )

        with pytest.raises(KeyError) as error:
            field.parse({})

        assert field.error(error.value) == {"error": "code_1", "field-key": "output"}
