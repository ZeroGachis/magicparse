from io import BytesIO
from typing import Any, Dict, List, Tuple, Union

from .callbacks import OnInvalidRowCallback, OnValidRowCallback
from .schema import Schema, builtins as builtins_schemas
from .post_processors import PostProcessor, builtins as builtins_post_processors
from .pre_processors import PreProcessor, builtins as builtins_pre_processors
from .transform import Transform
from .type_converters import TypeConverter, builtins as builtins_type_converters
from .validators import Validator, builtins as builtins_validators


__all__ = [
    "TypeConverter",
    "parse",
    "PostProcessor",
    "PreProcessor",
    "Schema",
    "Validator",
]


def parse(
    data: Union[bytes, BytesIO], schema_options: Dict[str, Any]
) -> Tuple[List[dict], List[dict]]:
    schema_definition = Schema.build(schema_options)
    return schema_definition.parse(data)


def stream_parse(
    data: Union[bytes, BytesIO],
    schema_options: Dict[str, Any],
    on_valid_parsed_row: OnValidRowCallback,
    on_invalid_parsed_row: OnInvalidRowCallback,
) -> None:
    schema_definition = Schema.build(schema_options)
    return schema_definition.stream_parse(
        data=data,
        on_valid_parsed_row=on_valid_parsed_row,
        on_invalid_parsed_row=on_invalid_parsed_row,
    )


Registrable = Union[Schema, Transform]


def register(items: Union[Registrable, List[Registrable]]) -> None:
    if not isinstance(items, list):
        items = [items]

    for item in items:
        if issubclass(item, Schema):
            Schema.register(item)
        elif issubclass(item, TypeConverter):
            TypeConverter.register(item)
        elif issubclass(item, PostProcessor):
            PostProcessor.register(item)
        elif issubclass(item, PreProcessor):
            PreProcessor.register(item)
        elif issubclass(item, Validator):
            Validator.register(item)
        else:
            raise ValueError(
                "transforms must be a subclass of Transform (or a list of it)"
            )


register(builtins_schemas)
register(builtins_pre_processors)
register(builtins_type_converters)
register(builtins_validators)
register(builtins_post_processors)
