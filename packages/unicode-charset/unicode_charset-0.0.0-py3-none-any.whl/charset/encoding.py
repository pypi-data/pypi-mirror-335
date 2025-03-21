import encodings
from collections.abc import Generator
from encodings.aliases import aliases
from typing import TypeVar

T = TypeVar("T")


class Singleton(type):
    """Metaclass to create singleton classes."""

    _instances: dict[type[T], T] = {}

    def __call__(cls: type[T], *args, **kwargs) -> T:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class ValidEncodings(metaclass=Singleton):

    def __contains__(self, item: str) -> bool:
        return encodings.search_function(item) is not None

    def __call__(self, item: str) -> bool:
        return item in self


class AllEncodings(metaclass=Singleton):
    _encoding = set(sorted(aliases.values()))

    def __iter__(self) -> Generator[str, None, None]:
        yield from self._encoding

    def __call__(self) -> set[str]:
        return self._encoding

    def __contains__(self, item: str) -> bool:
        return item in self._encoding


valid_encodings = ValidEncodings()
"""A set of all valid encoding names."""

all_encodings = AllEncodings()
"""A set of all available encoding names."""
