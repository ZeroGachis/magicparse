# magicparse 🛸

Declarative parser for structured data files.

## Table of contents

- [Getting started](#getting-started)
  - [Dev requirements](#dev-requirements)
- [Usage](#usage)
  - [Parse content](#parse-content)
  - [Register a custom transform](#register-custom-transform)
  - [Register a custom schema](#register-custom-schema)
  - [Stream parsing](#stream-parsing)
  - [Custom encoding](#custom-encoding)
- [API Reference](#api-reference)
 - [File types](#file-types)
 - [Types](#types)
 - [Computed fields](#computed-fields)
 - [Return types](#return-types)
 - [Error handling](#error-handling)
- [License](#license)

<a id="getting-started"></a>

## Getting started

📝 We recommend you to take time to read this README entirely before doing
anything to have a good overview of what you are going to do and avoid to
wrongly anticipate any steps.

<a id="dev-requirements"></a>

### Dev requirements

After this point we expect you to have [mise](https://mise.jdx.dev/) installed on your machine.

Use mise to install Python and poetry

```shell
mise install

# You can then test that they are available 
python --version
poetry --version
```

Install the python dev dependencies and setup pre-commit hooks

```shell
poetry install
pre-commit install
```

<a id="usage"></a>

## Usage

<a id="parse-content"></a>

### Parse content



```python
import magicparse


schema = {
    "file_type": "csv",
    "has_header": False,
    "delimiter": ";",
    "fields": [
        {
            "key": "ean",
            "column-number": 2,
            "type": "str",
            "validators": [
                {
                    "name": "regex-matches",
                    "parameters": {"pattern": "^\\d{13}$"},
                }
            ],
        },
        {"key": "label", "column-number": 3, "type": "str"},
        {"key": "family-code", "column-number": 8, "type": "str"},
        {
            "key": "vat",
            "column-number": 10,
            "type": "decimal",
            "optional": False,
        },
        {
            "key": "initial-price",
            "column-number": 11,
            "type": "decimal",
            "post-processors": [
                {
                    "name": "divide",
                    "parameters": {"denominator": 100},
                },
                {
                "name": "round",
                "parameters": {"precision": 3},
                }
            ]
        },
        {
            "key": "unit-of-measurement",
            "column-number": 12,
            "type": "int",
            "pre-processors": [
                {
                    "name": "map",
                    "parameters": {"values": {"K": 0, "A": 1, "L": 2}},
                }
            ],
        }
    ],
    "computed-fields": [
        {
            "key": "code",
            "type": "str",
            "builder": {
                "name": "concat",
                "parameters": {"fields": ["code_1", "code_2"]},
            }
        },
        {
            "key": "volume",
            "type": "decimal",
            "builder": {
                "name": "divide",
                "parameters": {
                    "numerator": "price",
                    "denominator": "price_by_unit",
                },
            }
        },
        {
            "key": "price_by_unit",
            "type": "decimal",
            "builder": {
                "name": "multiply",
                "parameters": {
                    "x_factor": "price",
                    "y_factor": "unit",
                }
            }
        }
    ],
}


rows = magicparse.parse(data="...", schema=schema)
```


<a id="register-custom-transform"></a>

### Register a custom transform

```python
from uuid import UUID
import magicparse

class GuidConverter(magicparse.TypeConverter):
    @staticmethod
    def key() -> str:
        return "guid"

    def apply(self, value):
        return UUID(value)


magicparse.register(GuidConverter)

schema = {
    "file_type": "csv",
    "fields": [
        {"key": "shop-guid", "type": "guid", "column-number": 1}
    ],
}

rows = magicparse.parse("13ec10cc-cc7e-4ee9-b091-9caa6d11aeb2", schema)
assert rows == [{"shop-guid": "13ec10cc-cc7e-4ee9-b091-9caa6d11aeb2"}]
```

<a id="register-custom-schema"></a>

### Register a custom schema

```python
import magicparse

class PipedSchema(magicparse.Schema):
    @staticmethod
    def key() -> str:
        return "piped"

    def get_reader(self, stream):
        for item in stream.read().split("|"):
            yield [item]

magicparse.register(PipedSchema)

schema = {
    "file_type": "piped",
    "fields": [
        {"key": "name", "type": "str", "column-number": 1}
    ]
}

rows = magicparse.parse("Joe|William|Jack|Averell", schema)
assert rows == [{"name": "Joe"}, {"name": "William"}, {"name": "Jack"}, {"name": "Averell"}]
```

<a id="stream-parsing"></a>

### Stream parsing

For large files, you can use streaming to process data incrementally:

```python
import magicparse

schema = {
    "file_type": "csv",
    "fields": [
        {"key": "name", "type": "str", "column-number": 1}
    ]
}

# Process data in chunks
for row in magicparse.stream_parse(data="...", schema=schema):
    match row:
        case magicparse.RowParsed(values):  
            print(f"The values {values}.")
        case magicparse.RowFailed(errors):
            print(f"The errors {errors}.")
        case magicparse.RowSkipped(reason):
            print(f"The errors {errors}.")
        case _:  
            print("Unknown type of row.")
```

<a id="custom-encoding"></a>

### Custom encoding

By default, magicparse uses UTF-8 encoding. You can specify a different encoding:

```python
schema = {
    "file_type": "csv",
    "encoding": "iso8859_5",  # or any other encoding
    "fields": [
        {"key": "name", "type": "str", "column-number": 1}
    ]
}
```

<a id="api-reference"></a>

## API Reference

<a id="file-types"></a>

### File types

- CSV (with or without header)
- Columnar

<a id="types"></a>

### Types

- str
- int
- decimal
- datetime (timezone aware)
- time (timezone aware)

#### Pre-processors

- left-pad-zeroes
- map
- regex-extract
- replace
- strip-whitespaces
- left-strip

#### Validators

- regex-matches
- greater-than
- not-null-or-empty

#### Post-processors

- divide
- round

<a id="computed-fields"></a>

### Computed Fields

Types, Pre-processors, Post-processors and validator is same as Field

#### Builder

- concat
- divide
- multiply
- coalesce

<a id="return-types"></a>

### Return Types

The parser returns a list of row objects:

- **`RowParsed`**: Successfully parsed row with `values` dict
- **`RowFailed`**: Failed to parse row with `errors` message
- **`RowSkipped`**: Skipped row with `errors` message

<a id="error-handling"></a>

### Error Handling

You can configure error handling for types, validators, and processors:

```python
{
    "key": "price",
    "type": {
        "key": "decimal",
        "nullable": True,  # Allow null values
        "on-error": "skip-row"  # Skip on error instead of raising
    }
}
```

Error handling options:
- `"raise"` (default): Raise exception on error
- `"skip-row"`: Skip the row and continue processing

<a id="license"></a>

## License

This project is licensed under the MIT License.
