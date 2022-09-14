from abc import ABC, abstractmethod


class PreProcessor(ABC):
    @classmethod
    def build(cls, options: dict) -> "PreProcessor":
        pre_processor = _pre_processors[options["name"]]

        if "parameters" in options:
            return pre_processor(**options["parameters"])
        else:
            return pre_processor()

    @abstractmethod
    def apply(value: str) -> str:
        pass


class LeftPadZeroes(PreProcessor):
    def __init__(self, width: int) -> None:
        self.width = width

    def apply(self, value: str) -> str:
        return value.zfill(self.width)


class Map(PreProcessor):
    def __init__(self, values: dict) -> None:
        self.values = values

    def apply(self, value: str) -> str:
        try:
            return self.values[value]
        except KeyError:
            keys = ", ".join(f"'{key}'" for key in self.values.keys())
            raise KeyError(f"value '{value}' does not map to any values in [{keys}]")


class Replace(PreProcessor):
    def __init__(self, pattern: str, replacement: str) -> None:
        self.pattern = pattern
        self.replacement = replacement

    def apply(self, value: str) -> str:
        return value.replace(self.pattern, self.replacement)


class StripWhitespaces(PreProcessor):
    def apply(self, value: str) -> str:
        return value.strip()


_pre_processors = {
    "left-pad-zeroes": LeftPadZeroes,
    "map": Map,
    "replace": Replace,
    "strip-whitespaces": StripWhitespaces,
}
