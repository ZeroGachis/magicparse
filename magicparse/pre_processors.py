import re
from .transform import Transform, OnError


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

        on_error = options.get("on-error", OnError.RAISE)
        if "parameters" in options:
            return pre_processor(on_error=on_error, **options["parameters"])
        else:
            return pre_processor(on_error=on_error)


class LeftPadZeroes(PreProcessor):
    def __init__(self, on_error: OnError, width: int) -> None:
        super().__init__(on_error)
        self.width = width

    def apply(self, value: str) -> str:
        return value.zfill(self.width)

    @staticmethod
    def key() -> str:
        return "left-pad-zeroes"


class Map(PreProcessor):
    def __init__(self, on_error: OnError, values: dict) -> None:
        super().__init__(on_error)
        self.values = values
        self._keys = ", ".join(f"'{key}'" for key in self.values.keys())

    def apply(self, value: str) -> str:
        try:
            return self.values[value]
        except:
            raise ValueError(
                f"value '{value}' does not map to any values in [{self._keys}]"
            )

    @staticmethod
    def key() -> str:
        return "map"


class Replace(PreProcessor):
    def __init__(self, on_error: OnError, pattern: str, replacement: str) -> None:
        super().__init__(on_error)
        self.pattern = pattern
        self.replacement = replacement

    def apply(self, value: str) -> str:
        return value.replace(self.pattern, self.replacement)

    @staticmethod
    def key() -> str:
        return "replace"


class StripWhitespaces(PreProcessor):
    def apply(self, value: str) -> str:
        return value.strip()

    @staticmethod
    def key() -> str:
        return "strip-whitespaces"


class LeftStrip(PreProcessor):
    def __init__(self, on_error: OnError, characters: str) -> None:
        super().__init__(on_error)
        self.characters = characters

    def apply(self, value: str) -> str:
        return value.lstrip(self.characters)

    @staticmethod
    def key() -> str:
        return "left-strip"


class RegexExtract(PreProcessor):
    def __init__(self, on_error: OnError, pattern: str) -> None:
        super().__init__(on_error)
        pattern = re.compile(pattern)
        if "value" not in pattern.groupindex:
            raise ValueError(
                "regex-extract's pattern must contain a group named 'value'"
            )

        self.pattern = pattern

    def apply(self, value: str) -> str:
        match = re.match(self.pattern, value)
        if not match:
            raise ValueError(
                f"cannot extract value from pattern '{self.pattern.pattern}'"
            )

        return match.group("value")

    @staticmethod
    def key() -> str:
        return "regex-extract"


builtins = [LeftPadZeroes, Map, RegexExtract, Replace, StripWhitespaces, LeftStrip]
