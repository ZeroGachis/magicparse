from abc import ABC, abstractmethod


class PreProcessor(ABC):
    @classmethod
    def build(cls, options: dict) -> "PreProcessor":
        try:
            name = options["name"]
        except:
            raise ValueError("pre-processor must have a 'name' key")

        try:
            pre_processor = _pre_processors[name]
        except:
            raise ValueError(f"invalid pre-processor '{name}'")

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
        self._keys = ", ".join(f"'{key}'" for key in self.values.keys())

    def apply(self, value: str) -> str:
        try:
            return self.values[value]
        except:
            raise ValueError(
                f"value '{value}' does not map to any values in [{self._keys}]"
            )


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
