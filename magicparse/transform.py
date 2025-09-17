from abc import ABC, abstractclassmethod, abstractmethod, abstractstaticmethod
from typing import Any

from .parsed_field import LastTransformSuccess, LastTransformFailed


class Transform(ABC):
    def __init__(self, on_error: str) -> None:
        self.on_error = on_error

    @abstractclassmethod
    def build(cls, options: dict) -> "Transform":
        pass

    def apply(
        self, last_transform_result: LastTransformSuccess | LastTransformFailed | None
    ) -> LastTransformSuccess | LastTransformFailed | None:
        if last_transform_result is None:
            return None

        if isinstance(last_transform_result, LastTransformFailed):
            return last_transform_result

        try:
            return LastTransformSuccess(
                value=self.transform(last_transform_result.value)
            )
        except Exception as e:
            if self.on_error == "skip-row":
                return LastTransformFailed(skip_row=True)
            raise e

    @abstractmethod
    def transform(self, value: Any | None) -> Any | None:
        pass

    @abstractstaticmethod
    def key() -> str:
        pass

    @classmethod
    def register(cls, transform: "Transform") -> None:
        if not hasattr(cls, "registry"):
            cls.registry = {}

        cls.registry[transform.key()] = transform
