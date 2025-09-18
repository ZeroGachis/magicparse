from io import BytesIO

from .schema import (
    RowParsed,
    RowFailed,
    RowSkipped,
    Schema,
    builtins as builtins_schemas,
)
from .post_processors import PostProcessor, builtins as builtins_post_processors
from .pre_processors import PreProcessor, builtins as builtins_pre_processors
from .builders import (
    Builder,
    builtins as builtins_composite_processors,
)
from .transform import Transform
from .type_converters import TypeConverter, builtins as builtins_type_converters
from typing import Any, Dict, Iterable, List, Union
from .validators import Validator, builtins as builtins_validators


__all__ = [
    "TypeConverter",
    "parse",
    "stream_parse",
    "PostProcessor",
    "PreProcessor",
    "Schema",
    "RowParsed",
    "RowSkipped",
    "RowFailed",
    "Validator",
]


def parse(
    data: Union[bytes, BytesIO], schema_options: Dict[str, Any]
) -> List[RowParsed | RowSkipped | RowFailed]:
    schema_definition = Schema.build(schema_options)
    return schema_definition.parse(data)


def stream_parse(
    data: Union[bytes, BytesIO], schema_options: Dict[str, Any]
) -> Iterable[RowParsed | RowSkipped | RowFailed]:
    schema_definition = Schema.build(schema_options)
    return schema_definition.stream_parse(data)


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
        elif issubclass(item, Builder):
            Builder.register(item)
        else:
            raise ValueError(
                "transforms must be a subclass of Transform (or a list of it)"
            )


register(builtins_schemas)
register(builtins_pre_processors)
register(builtins_type_converters)
register(builtins_validators)
register(builtins_post_processors)
register(builtins_composite_processors)
