# magicparse 🛸

Declarative parser

## Usage

### Parse content

```python
import magicparse


schema = {
    "file_type": "csv",
    "has_header": False,
    "delimiter": ";",
    "fields": [
        {"key": "ean", "column-number": 2, "type": "str", "validators": [{"name": "regex-matches", "parameters": {"pattern": "^\\d{13}$"}}]},
        {"key": "label", "column-number": 3, "type": "str"},
        {"key": "family-code", "column-number": 8, "type": "str"},
        {"key": "vat", "column-number": 10, "type": "decimal"},
        {"key": "initial-price", "column-number": 11, "type": "decimal", "post-processors": {"name": "divide", "parameters": {"denominator": 100}}},
        {"key": "unit-of-measurement", "column-number": 12, "type": "int", "pre-processors": [{"name": "map", "parameters": {"values": {"K": 0, "A": 1, "L": 2}}}]},
        {"key": "volume", "column-number": 13, "type": "decimal"},
    ]
}


rows, errors= magicparse.parse(data="...", schema=schema)
```


### Register a custom transform and parse content

```python
from uuid import UUID
import magicparse

class GuidConverter(magicparse.Converter):
    def key() -> str:
        return "guid"

    def apply(self, value):
        return UUID(value)


magicparse.register(GuidConverter)

schema = Schema.build(
    {
        "file_type": "csv",
        "fields": [{"key": "shop-guid", "type": "guid", "column-number": 1}],
    }
)

rows, errors = schema.parse("13ec10cc-cc7e-4ee9-b091-9caa6d11aeb2")
assert rows == [{"shop-guid": "13ec10cc-cc7e-4ee9-b091-9caa6d11aeb2"}]
assert not errors
```

## API

### File types

- CSV (with or without header)
- Columnar

### Fields

#### Types

- str
- int
- decimal

#### Pre-processors

- left-pad-zeroes
- map
- replace
- strip-whitespaces

#### Validators

- regex-matches

#### Post-processors

- divide
