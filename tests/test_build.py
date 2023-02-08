import pytest

from pyntegrant.initializer import Initializer
from pyntegrant.loaders import (
    from_json,
    from_jsons,
    from_toml,
    from_tomls,
    replace_refs,
)
from pyntegrant.map import PRef, build
from pyntegrant.system import System

quad_config = dict(
    numerator=dict(minuend=PRef("bsqr"), subtrahend=PRef("ac4")),
    denominator=1,
    bsqr=4,
    result=dict(numerator=PRef("numerator"), denominator=PRef("denominator")),
    ac4=dict(a=1, c=2),
)

quad_config_tobuild = dict(
    numerator=dict(minuend="#p/ref bsqr", subtrahend="#p/ref ac4"),
    denominator=1,
    bsqr=4,
    result=dict(numerator="#p/ref numerator", denominator="#p/ref denominator"),
    ac4=dict(a=1, c=2),
)

quad_config_json = """
{ "numerator" : { "minuend" : "#p/ref bsqr", "subtrahend" : "#p/ref ac4" },
  "denominator" : 1,
  "bsqr" : 4,
  "result" : { "numerator" : "#p/ref numerator", "denominator" : "#p/ref denominator" },
  "ac4" : { "a" : 1, "c" : 2 }
}
"""

quad_config_toml = """
denominator=1
bsqr=4

result.numerator = "#p/ref numerator"
result.denominator = "#p/ref denominator"

[numerator]
minuend="#p/ref bsqr"
subtrahend="#p/ref ac4"

[ac4]
a=1
c=2
"""


def initializer() -> Initializer:
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

    return i


@pytest.mark.parametrize(
    "config, expected",
    # (b^2 - 4ac)/2a
    [
        (
            quad_config,
            4,
        )
    ],
)
def test_build(config, expected, keys=None):
    i = initializer()
    system = build(config, config.keys() if keys is None else keys, i.initialize)
    print(system)
    assert system["result"] == expected

    system = System.from_config(config, i, keys)
    assert system.result == expected


def test_extra_argument():
    config = quad_config.copy()
    config["extra"] = 42
    i = initializer()
    # this will fail with 'extra' in there... unless we don't ask for
    # it and only ask for the dependencies that are used.
    system = build(config, {"result"}, i.initialize)


@pytest.mark.parametrize(
    "config, expected",
    # (b^2 - 4ac)/2a
    [
        (
            quad_config_tobuild,
            4,
        )
    ],
)
def test_build_system(config, expected):
    test_build(replace_refs(config), expected)


@pytest.mark.parametrize(
    "config, expected",
    # (b^2 - 4ac)/2a
    [
        (
            quad_config_tobuild,
            4,
        )
    ],
)
def test_load_system(config, expected):
    test_build(replace_refs(config), expected)


@pytest.mark.parametrize("config, expected", [(quad_config_json, 4)])
def test_load_json(config, expected):
    test_build(from_jsons(config), expected)


@pytest.mark.parametrize("config, expected", [(quad_config_toml, 4)])
def test_load_toml(config, expected):
    test_build(from_tomls(config), expected)


def initializer_with_default():

    result = Initializer()

    @result.register_default()
    def _(value):
        return value

    @result.register("result")
    def _(s):
        return s.upper()

    return result


def test_initializer_with_default():
    config = replace_refs(dict(foo="foo", bar="bar", result="#p/ref foo"))
    i = initializer_with_default()
    system = build(config, {"result"}, i.initialize)
    assert system["result"] == "FOO"
