# csvmagic 🛸

Declarative parser for CSV and columnar data

## Usage

```python
import csvmagic


schema = {
    "file_type": "csv",
    "has_header": False,
    "delimiter": ";",
    "fields": [
        {"key": "ean", "column-number": 2, "type": "str", "validators": [{"name": "regex-matches", "parameters": {"pattern": "^\\d{13}$"}}]},
        {"key": "label", "column-number": 3, "type": "str"},
        {"key": "family-code", "column-number": 8, "type": "str"},
        {"key": "vat", "column-number": 10, "type": "decimal"},
        {"key": "initial-price", "column-number": 11, "type": "decimal"},
        {"key": "unit-of-measurement", "column-number": 12, "type": "int", "pre-processors": [{"name": "map", "parameters": {"values": {"K": 0, "A": 1, "L": 2}}}]},
        {"key": "volume", "column-number": 13, "type": "decimal"},
    ]
}


rows, errors= csvmagic.parse(data="...", schema=schema)
```
