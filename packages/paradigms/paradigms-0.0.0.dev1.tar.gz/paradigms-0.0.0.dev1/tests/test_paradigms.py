from testfixtures import compare

from paradigms.core import Paradigms
from paradigms.stdlib import Simple


def add(x: int, y: int) -> int:
    return x + y


def test_minimal() -> None:
    compare(Paradigms()(add)(1, 2), expected=3)


def test_explicit() -> None:
    paradigms = Paradigms()
    caller = paradigms(add)
    result = caller(1, 2)
    compare(result, expected=3)


def test_shift() -> None:
    paradigms = Paradigms()
    caller = paradigms.get(add, paradigm=Simple)
    result = caller(1, 2)
    compare(result, expected=3)
