from .transform import Transform


class PreProcessor(Transform):
    @classmethod
    def build(cls, options: dict) -> "PreProcessor":
        try:
            name = options["name"]
        except:
            raise ValueError("pre-processor must have a 'name' key")

        try:
            pre_processor = cls.registry[name]
        except:
            raise ValueError(f"invalid pre-processor '{name}'")

        if "parameters" in options:
            return pre_processor(**options["parameters"])
        else:
            return pre_processor()


class LeftPadZeroes(PreProcessor):
    def __init__(self, width: int) -> None:
        self.width = width

    def apply(self, value: str) -> str:
        return value.zfill(self.width)

    def key() -> str:
        return "left-pad-zeroes"


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

    def key() -> str:
        return "map"


class Replace(PreProcessor):
    def __init__(self, pattern: str, replacement: str) -> None:
        self.pattern = pattern
        self.replacement = replacement

    def apply(self, value: str) -> str:
        return value.replace(self.pattern, self.replacement)

    def key() -> str:
        return "replace"


class StripWhitespaces(PreProcessor):
    def apply(self, value: str) -> str:
        return value.strip()

    def key() -> str:
        return "strip-whitespaces"


builtins = [LeftPadZeroes, Map, Replace, StripWhitespaces]
