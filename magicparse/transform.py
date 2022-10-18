from abc import ABC, abstractclassmethod, abstractmethod, abstractstaticmethod


class Transform(ABC):
    @abstractclassmethod
    def build(cls, options: dict) -> "Transform":
        pass

    @abstractmethod
    def apply(self, value):
        pass

    @abstractstaticmethod
    def key() -> str:
        pass

    @classmethod
    def register(cls, transform: "Transform") -> None:
        if not hasattr(cls, "registry"):
            cls.registry = {}

        cls.registry[transform.key()] = transform
