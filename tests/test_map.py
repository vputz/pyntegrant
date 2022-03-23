import pprint

import networkx as nx
import pytest

from pyntegrant.map import (PRef, SystemMap, build, dependency_graph,
                            find_keys, transitive_dependencies,
                            transitive_dependencies_set)


def test_dependency_graph():
    m = dict(a=dict(arg1=1, arg2=PRef("b")), b=PRef("c"), c=1)
    g = dependency_graph(m)
    assert list(nx.topological_sort(g)) == ["a", "b", "c"]


# some sample graphs for dependency tests; see
# https://github.com/weavejester/dependency/blob/master/test/weavejester/dependency_test.clj
def g1() -> nx.DiGraph:
    result = nx.DiGraph()
    result.add_edges_from([("b", "a"), ("c", "b"), ("c", "a"), ("d", "c")])
    return result


def g2() -> nx.DiGraph:
    result = nx.DiGraph()
    result.add_edges_from([(2, 1), (3, 2), (4, 2), (4, 5), (6, 3), (7, 6), (7, 4)])
    return result


@pytest.mark.parametrize(
    "g, node, expected",
    [
        (g1(), "d", frozenset(("a", "b", "c"))),
        (g2(), 7, frozenset((2, 4, 6, 1, 5, 3))),
        (g2(), 3, frozenset((2, 1))),
        (g2(), 4, frozenset((1, 2, 5))),
    ],
)
def test_transitive_dependencies(g, node, expected):
    result = transitive_dependencies(g, node)
    assert result == expected


@pytest.mark.parametrize("g, nodes, expected", [(g2(), {3, 4}, frozenset((1, 2, 5)))])
def test_transitive_dependencies_set(g, nodes, expected):
    result = transitive_dependencies_set(g, nodes)
    assert result == expected


def m1() -> SystemMap:
    return {"a": {"arg1": 1, "arg2": PRef(key="c")}, "b": PRef(key="a"), "c": 1}


@pytest.mark.parametrize(
    "config, nodes, expected",
    [(m1(), {"a"}, ["c", "a"]), (m1(), {"b", "a"}, ["c", "a", "b"])],
)
def test_find_keys(config, nodes, expected):
    # this tests dependent_keys
    result = find_keys(config, nodes, transitive_dependencies_set)
    assert result == expected


# from https://github.com/weavejester/integrant/blob/32a46f5dca8a6b563a6dddf88bec887be3201b08/test/integrant/core_test.cljc#L476
@pytest.mark.parametrize(
    "config, expected",
    [
        (
            {"a": PRef("b"), "b": 1},
            (
                {"a": ["build", "a", ["build", "b", 1]], "b": ["build", "b", 1]},
                [["build", "b", 1], ["build", "a", ["build", "b", 1]]],
            ),
        )
    ],
)
def test_build(config, expected):
    def build_log(config: SystemMap):
        log = []

        def add_build_step(k, v):
            r = ["build", k, v]
            log.append(r)
            return r

        result = build(config, config.keys(), add_build_step)
        return (result, log)

    result = build_log(config)
    pprint.pprint(result)
    assert result == expected
