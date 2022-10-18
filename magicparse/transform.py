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
