import functools
import random
import unicodedata
from collections.abc import Generator
from sys import maxunicode
from typing import Optional


def _assert_args(
    min: Optional[int] = None,
    max: Optional[int] = None,
) -> tuple[int, int]:
    """Assert that the arguments are valid and return the min and max values."""

    if min is None:
        min = 0

    if max is None:
        max = maxunicode

    if not min < max:
        raise ValueError(f"{min=} must be less than {max=}")
    if max > maxunicode:
        raise ValueError(f"{max=} must be less than {maxunicode=}")
    if min < 0:
        raise ValueError(f"{min=} must be greater than or equal to 0")

    return min, max


def urandom(
    max: Optional[int] = None,
    min: Optional[int] = None,
) -> Generator[int, None, None]:
    """Generate random unicode numbers yielding each number only once.

    Generates unique random integers between min and max (inclusive) that can be used
    as Unicode code points.

    Args:
        max: Optional upper bound for the Unicode code point (inclusive).
            If None, uses `sys.maxunicode`. Defaults to None.
        min: Optional lower bound for the Unicode code point (inclusive).
            If None, starts from 0. Defaults to None.

    Yields:
        int: A random integer representing a Unicode code point.

    Raises:
        ValueError: If min is greater than or equal to max, or if max exceeds
            `sys.maxunicode`.
    """

    limit = max - min + 1

    seen = set()
    while len(seen) < limit:
        num = random.randint(min, max)
        if num not in seen:
            seen.add(num)
            yield num


def urange(
    max: Optional[int] = None,
    min: Optional[int] = None,
) -> Generator[int, None, None]:

    yield from range(min, max + 1)


def all_unicodes(
    names: bool = True,
    random: bool = True,
    **kwargs,
) -> Generator[tuple[str, str], None, None]:
    """Generate random Unicode characters with their names.

    Args:
        names: If True, only yield characters that have names in the Unicode
            database. If False, yield all characters. Defaults to True.
        **kwargs: Additional keyword arguments passed to randunicode()

    Yields:
        Tuple[str, str]: A tuple containing:
            - str: The Unicode character
            - str: The name of the character (empty string if no name exists)
    """

    min, max = _assert_args(**kwargs)

    if random:
        unicodes = functools.partial(urandom, max, min)
    else:
        unicodes = functools.partial(urange, max, min)

    for uni in map(chr, unicodes()):
        name = unicodedata.name(uni, "")
        if names and name == "":
            continue

        yield uni, name
