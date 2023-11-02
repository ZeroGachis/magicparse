from typing import Any, Dict, List, Protocol


class OnValidRowCallback(Protocol):
    def __call__(self, index: int, parsed_row: Dict[str, Any], raw_data: Any) -> None:
        ...


class OnInvalidRowCallback(Protocol):
    def __call__(self, errors_info: List[Dict[str, Any]], raw_data: Any) -> None:
        ...
