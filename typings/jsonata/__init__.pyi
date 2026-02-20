from collections.abc import Callable
from typing import Any, ClassVar

class Frame:
    def bind(self, name: str, val: Any) -> None: ...

class Jsonata:
    static_frame: ClassVar[Frame]
    validate_input: bool

    def __init__(self, expr: str) -> None: ...
    def evaluate(self, input: Any) -> Any: ...

    class JLambda:
        def __init__(self, function: Callable[..., Any]) -> None: ...
