"""Contains classes and functions related to
defining a mapping for pyntegrant which represents
a system
"""

from dataclasses import dataclass
from functools import reduce
from typing import Any, Mapping, NewType, Union

from networkx import DiGraph

from pyntegrant.helpers import depth_search, reduce_kv

Key = str


@dataclass(eq=True, frozen=True)
class PRef:
    key: str


SystemMap = Mapping[Key, Any]


def all_keys_valid(m: SystemMap) -> bool:
    """Whether all the keys in the map are of the Key (str) type"""
    return all((isinstance(k, Key) for k in m.keys()))


def all_refs_resolveable(m: SystemMap) -> bool:
    """Whether all refs (PRef classes) in the map resolve to
    keys.
    """
    refs = frozenset((v for v in m.values() if isinstance(v, PRef)))
    keys = frozenset(m.keys())
    return all((ref.key in keys for ref in refs))


def is_reflike(x: Any) -> bool:
    return isinstance(x, PRef)


def find_refs(v: Any):
    """Returns the names of keys that represent references in the collection v"""
    return frozenset(map(lambda x: x.key, depth_search(is_reflike, v)))


def add_dependency(g: DiGraph, a: Any, b: Any) -> DiGraph:
    """Adds an edge from a to b within g.  Returns g (mutated).

    This function modifies its input.
    """
    g.add_edge(a, b)
    return g


def dependency_graph(config: SystemMap) -> DiGraph:
    """Given a config, creates a directed graph representing dependencies.

    If a key A depends on anything involving a PRef(key="B"), this sets up
    a dependency "A depends on B".  The resulting digraph can be topologically
    sorted to determine an initialization order.  An edge ('A', 'B') in the digraph
    represents the dependency of A on B.
    """
    return reduce_kv(
        lambda g, k, v: reduce(
            lambda g2, v2: add_dependency(g2, k, v2), find_refs(v), g
        ),
        DiGraph(),
        config,
    )
