import pytest

from pyntegrant.initializer import Initializer
from pyntegrant.map import PRef, build


@pytest.mark.parametrize(
    "config, expected",
    # (b^2 - 4ac)/2a
    [
        (
            dict(
                numerator=dict(minuend=PRef("bsqr"), subtrahend=PRef("ac4")),
                denominator=1,
                bsqr=4,
                result=dict(
                    numerator=PRef("numerator"), denominator=PRef("denominator")
                ),
                ac4=dict(a=1, c=2),
            ),
            4,
        )
    ],
)
def test_build(config, expected):
    i = Initializer()

    @i.register("ac4")
    def _(a, c):
        return a * c * 4

    @i.register("bsqr")
    def _(b):
        return b * b

    @i.register("denominator")
    def _(a):
        return 2 * a

    @i.register("numerator")
    def _(minuend, subtrahend):
        return minuend - subtrahend

    @i.register("result")
    def _(numerator, denominator):
        return numerator / denominator

    system = build(config, config.keys(), i.initialize)
    print(system)
    assert system["result"] == expected
