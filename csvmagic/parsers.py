from .schema import Schema
from typing import List, Tuple


def parse(data: str, schema_options: dict) -> Tuple[List[dict], List[dict]]:
    schema = Schema.build(schema_options)

    reader = schema.get_reader(data)

    row_number = 0
    if schema.has_header:
        next(reader)
        row_number += 1

    result = []
    errors = []
    for row in reader:
        row_number += 1
        row_is_valid = True
        item = {}
        for field in schema.fields:
            try:
                value = field.read_value(row)
            except Exception as exc:
                errors.append({"row-number": row_number, **field.error(exc)})
                row_is_valid = False
                continue

            item[field.key] = value

        if row_is_valid:
            result.append(item)

    return result, errors
