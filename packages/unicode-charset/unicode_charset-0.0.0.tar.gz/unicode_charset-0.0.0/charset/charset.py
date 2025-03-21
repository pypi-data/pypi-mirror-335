from collections.abc import Generator
from typing import NamedTuple, Optional

from charset.encoding import all_encodings, valid_encodings
from charset.unicode import all_unicodes, maxunicode


class CharSet(NamedTuple):
    """Hold a character with its encoding and name."""

    encoding: str
    chr: str
    name: str

    def __str__(self) -> str:
        return self.chr

    @property
    def ord(self) -> int:
        return ord(self.chr)


def charset(
    encoding: str,
    n: Optional[int] = None,
    **kwargs,
) -> Generator[CharSet, None, None]:
    """Generate CharSet objects for characters that can be encoded in the specified
    encoding.

    Yields up to n unique CharSet objects for a given encoding

    Args:
        encoding: The name of the encoding to test characters against (e.g., 'utf-8').
        n: Number of characters to yield. Must be greater than 0. Defaults to 1.
        **kwargs: Additional keyword arguments passed to all_unicodes():

    Yields:
        CharSet: A named tuple containing:
            - encoding: The specified encoding name
            - char: The Unicode character
            - name: The Unicode character name
    """

    if encoding not in valid_encodings:
        raise ValueError(f"{encoding=} is not a valid encoding")

    if n and n < 1:
        raise ValueError(f"{n=} must be greater than 0")
    elif n is None:
        n = maxunicode

    i = 0

    for char, name in all_unicodes(**kwargs):
        try:
            _ = char.encode(encoding)
        except UnicodeEncodeError:
            continue
        except LookupError:
            break

        yield CharSet(encoding, char, name)

        i += 1
        if i >= n:
            break


def all_charsets(
    n: Optional[int] = None,
    **kwargs,
) -> Generator[CharSet, None, None]:
    """Generate n unique CharSet objects for all available encodings.

    Args:
        n: Number of characters to yield per encoding. Must be greater than 0.
            Defaults to 1.

    Yields:
        CharSet: A named tuple for each supported encoding containing:
            - encoding: The encoding name
            - char: A Unicode character that can be encoded
            - name: The Unicode character name
    """
    for encoding in all_encodings:
        yield from charset(encoding, n, **kwargs)
