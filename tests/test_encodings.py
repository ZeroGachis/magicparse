from unittest import TestCase

from magicparse import Schema


class TestCsvEncoding(TestCase):
    def test_default_encoding(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [{"key": "name", "type": "str", "column-number": 1}],
            }
        )

        rows, errors = schema.parse("José\n李\n💩\n".encode("utf-8"))

        assert len(errors) == 0
        assert rows == [{"name": "José"}, {"name": "李"}, {"name": "💩"}]

    def test_exotic_encoding(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "encoding": "iso8859_5",
                "fields": [{"key": "name", "type": "str", "column-number": 1}],
            }
        )

        rows, errors = schema.parse(
            "Да здравствует Владимир проклятый\n"
            "Да здравствует Карл Маркс\n"
            "Да здравствует Россия\n".encode("iso8859_5")
        )

        assert len(errors) == 0
        assert rows == [
            {"name": "Да здравствует Владимир проклятый"},
            {"name": "Да здравствует Карл Маркс"},
            {"name": "Да здравствует Россия"},
        ]


class TestExoticEncoding(TestCase):
    def test_default_encoding(self):
        schema = Schema.build(
            {
                "file_type": "columnar",
                "fields": [
                    {
                        "key": "name",
                        "type": "str",
                        "column-start": 0,
                        "column-length": 4,
                    }
                ],
            }
        )

        rows, errors = schema.parse("José\n李   \n💩   \n".encode("utf-8"))

        assert len(errors) == 0
        assert rows == [{"name": "José"}, {"name": "李   "}, {"name": "💩   "}]

    def test_exotic_encoding(self):
        schema = Schema.build(
            {
                "file_type": "columnar",
                "encoding": "iso8859_5",
                "fields": [
                    {
                        "key": "name",
                        "type": "str",
                        "column-start": 0,
                        "column-length": 33,
                    }
                ],
            }
        )

        rows, errors = schema.parse(
            "Да здравствует Владимир проклятый\n"
            "Да здравствует Карл Маркс        \n"
            "Да здравствует Россия            \n".encode("iso8859_5")
        )

        assert len(errors) == 0
        assert rows == [
            {"name": "Да здравствует Владимир проклятый"},
            {"name": "Да здравствует Карл Маркс        "},
            {"name": "Да здравствует Россия            "},
        ]
