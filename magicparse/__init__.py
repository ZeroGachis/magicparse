from .schema import Schema
from .post_processors import PostProcessor, builtins as builtins_post_processors
from .pre_processors import PreProcessor, builtins as builtins_pre_processors
from .transform import Transform
from .type_converters import TypeConverter, builtins as builtins_type_converters
from typing import Any, Dict, List, Tuple, Union
from .validators import Validator, builtins as builtins_validators


__all__ = [
    "TypeConverter",
    "parse",
    "PostProcessor",
    "PreProcessor",
    "Schema",
    "Validator",
]


def parse(data: str, schema_options: Dict[str, Any]) -> Tuple[List[dict], List[dict]]:
    schema = Schema.build(schema_options)
    return schema.parse(data)


def register(transforms: Union[Transform, List[Transform]]) -> None:
    if isinstance(transforms, Transform):
        transforms = [transforms]

    for transform in transforms:
        if issubclass(transform, TypeConverter):
            TypeConverter.register(transform)
        elif issubclass(transform, PostProcessor):
            PostProcessor.register(transform)
        elif issubclass(transform, PreProcessor):
            PreProcessor.register(transform)
        elif issubclass(transform, Validator):
            Validator.register(transform)
        else:
            raise ValueError(
                "transforms must be a subclass of Transform (or a list of it)"
            )


register(builtins_pre_processors)
register(builtins_type_converters)
register(builtins_validators)
register(builtins_post_processors)
