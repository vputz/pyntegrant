import pytest

from pyntegrant.initializer import Initializer

i = Initializer()


@i.register("teststr")
def _(v):
    return v + "!!"


@i.register("testint")
def _(v):
    return v * 2


@i.register("division")
def _(dividend, divisor):
    return dividend / divisor


@pytest.mark.parametrize(
    "key, arg, expected",
    [
        ("teststr", "a", "a!!"),
        ("teststr", "b", "b!!"),
        ("testint", 0, 0),
        ("testint", 1, 2),
        ("division", dict(dividend=6, divisor=2), 3),
    ],
)
def test_initializer(key, arg, expected):
    f = i.initialize
    assert f(key, arg) == expected
