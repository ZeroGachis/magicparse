from unittest import TestCase

from magicparse import Schema
from magicparse.schema import RowParsed


class TestCsvEncoding(TestCase):
    def test_default_encoding(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "fields": [{"key": "name", "type": "str", "column-number": 1}],
            }
        )

        rows = schema.parse("José\n李\n💩\n".encode("utf-8"))

        assert rows == [
            RowParsed(row_number=1, values={"name": "José"}),
            RowParsed(row_number=2, values={"name": "李"}),
            RowParsed(row_number=3, values={"name": "💩"}),
        ]

    def test_exotic_encoding(self):
        schema = Schema.build(
            {
                "file_type": "csv",
                "encoding": "iso8859_5",
                "fields": [{"key": "name", "type": "str", "column-number": 1}],
            }
        )

        rows = schema.parse(
            "Да здравствует Владимир проклятый\n"
            "Да здравствует Карл Маркс\n"
            "Да здравствует Россия\n".encode("iso8859_5")
        )

        assert rows == [
            RowParsed(
                row_number=1, values={"name": "Да здравствует Владимир проклятый"}
            ),
            RowParsed(
                row_number=2, values={"name": "Да здравствует Карл Маркс"}
            ),
            RowParsed(
                row_number=3, values={"name": "Да здравствует Россия"}
            ),
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

        rows = schema.parse("José\n李   \n💩   \n".encode("utf-8"))

        assert rows == [
            RowParsed(row_number=1, values={"name": "José"}),
            RowParsed(row_number=2, values={"name": "李   "}),
            RowParsed(row_number=3, values={"name": "💩   "}),
        ]

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

        rows = schema.parse(
            "Да здравствует Владимир проклятый\n"
            "Да здравствует Карл Маркс        \n"
            "Да здравствует Россия            \n".encode("iso8859_5")
        )

        assert rows == [
            RowParsed(
                row_number=1,
                values={"name": "Да здравствует Владимир проклятый"}
            ),
            RowParsed(
                row_number=2,
                values={"name": "Да здравствует Карл Маркс        "}
            ),
            RowParsed(
                row_number=3,
                values={"name": "Да здравствует Россия            "}
            ),
        ]
