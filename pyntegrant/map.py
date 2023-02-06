"""Contains classes and functions related to
defining a mapping for pyntegrant which represents
a system
"""

from dataclasses import dataclass
from functools import partial, reduce
from typing import Any, Callable, Iterable, KeysView, Mapping, NewType, Union

import networkx as nx
from icontract import ensure, require
from networkx import DiGraph
from pyrsistent import pmap

from pyntegrant.helpers import depth_search, postwalk, reduce_kv

Key = str


@dataclass(eq=True, frozen=True)
class PRef:
    """A marker class, used in dict-based config values to refer to a key."""

    key: str


SystemMap = Mapping[Key, Any]
Keyset = Union[frozenset[Key], KeysView]


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
    return reduce_kv(  # type:ignore
        lambda g, k, v: reduce(
            lambda g2, v2: add_dependency(g2, k, v2), find_refs(v), g
        ),
        DiGraph(),
        config,
    )


# There was a requirement that all nodes in the config be in the
# dependency graph; that's no longer the case because it allows you to
# have "orphan keys" so that you can have multiple options, eg
# { "a": 3, "b": 4, "c": "#p/ref a" } and transitive_dependencies won't barf because b
# exists but isn't in the dependency graph since nothing depends on it
# @require(lambda g, node: node in g)
@ensure(lambda result, g: all([n in g for n in result]))
def transitive_dependencies(g: DiGraph, node: Any) -> frozenset[Any]:
    """The set of all things which any node in node-set depends on"""
    return frozenset(nx.descendants(g, node)) if node in g else frozenset()


# see note on transitive_dependencies
# @require(lambda g, nodes: [node in g for node in nodes])
@ensure(lambda result, g: all([n in g for n in result]))
def transitive_dependencies_set(g: DiGraph, nodes: Keyset) -> Keyset:
    """The set of all things which any node in nodes depends on,
    directly or transitively
    """
    dependent_nodes = frozenset({n for n in nodes if n in g})
    return frozenset.union(
        *[transitive_dependencies(g, node) for node in dependent_nodes]
    )


def find_keys(
    config: SystemMap, keys: Keyset, f: Callable[[DiGraph, Keyset], Keyset]
) -> list[Key]:
    """Return the union of keys and f(config, keys), topologically sorted
    so that the last item in the list depends on everything before it"""
    g = dependency_graph(config)
    fkeys = frozenset(f(g, keys))
    result = frozenset.union(frozenset(keys), fkeys)
    sorted_nodes = list(nx.topological_sort(g))
    return sorted(result, key=lambda x: sorted_nodes.index(x), reverse=True)


def dependent_keys(config: SystemMap, keys: Keyset) -> list[Key]:
    return find_keys(config, keys, transitive_dependencies_set)


def select_keys(config: SystemMap, keys: Iterable[Key]) -> SystemMap:
    return pmap({k: config[k] for k in keys})


@require(lambda ref, config: ref.key in config)
def ref_resolve(ref: PRef, config: SystemMap, resolvef: Callable[[Key, Any], Any]):
    """Resolves the reference in the given config.

    This is slightly more complicated than it needs to be; more than
    necessary for the simple version of Integrant we're building here, but
    less complicated than necessary for the full version of Integrant.  Expect
    modification either way in the future.
    """
    return resolvef(ref.key, config.get(ref.key))


def expand_key(config: SystemMap, resolvef: Callable[[Key, Any], Any], v: Any) -> Any:
    """Walks the value, resolving all refs within using the passed function and the given
    config (a typical resolvef could be lambda k,v: v)"""
    return postwalk(
        lambda x: ref_resolve(x, config, resolvef) if is_reflike(x) else x, v
    )


@ensure(lambda result, k, v: result[k] == v)
def assoc(system: SystemMap, k: Key, v: Any):
    return pmap(system).update(pmap({k: v}))


def build_key(
    buildfn: Callable[[Key, Any], Any],
    resolvef: Callable[[Key, Any], Any],
    system: SystemMap,
    kv: tuple[Key, Any],
) -> SystemMap:
    k, v = kv
    expanded_value = expand_key(system, resolvef, v)
    built_value = buildfn(k, expanded_value)
    return assoc(system, k, built_value)


def build(config: SystemMap, keys: Keyset, f: Callable[[Key, Any], Any]) -> SystemMap:
    """Apply function f to each (key, value) pair in a configuration map,
    traversing keys in dependency order and expanding any references in the value.

    The function should take two arguments, a key and value, and return a new value.

    Todo: An optional fourth argument, assertf, may be supplied to provide an
    assertion check on the system, key, and expanded value.
    """
    relevant_keys = dependent_keys(config, keys)
    relevant_config = select_keys(config, relevant_keys)
    resolvef = lambda k, v: v
    return pmap(
        reduce(
            partial(build_key, f, resolvef),  # type:ignore
            ((k, config[k]) for k in relevant_keys),
            {},
        ),
    )
