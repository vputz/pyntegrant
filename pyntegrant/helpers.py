"""A collection of helper functions; many are
related to functions in Clojure.
"""

from collections import deque
from collections.abc import Iterable
from functools import partial, reduce
from typing import Any, Callable, Generator, Mapping, Sequence, TypeVar

from icontract import require


def is_seq(x: Any) -> bool:
    """Modification of clojure to loop over sequences,
    but views a map as a sequence (.items())
    """
    return (isinstance(x, Sequence) or isinstance(x, Mapping)) and not (
        isinstance(x, str)
    )


@require(lambda x: is_seq(x))
def seq(x: Any) -> Iterable:
    """Transforms x into an iterable sequence.  Maps are
    transformed into iterations of (k,v) pairs
    """
    if isinstance(x, Sequence):
        return x
    elif isinstance(x, Mapping):
        return x.items()
    else:
        assert False


def tree_seq(
    is_branch: Callable[[Any], bool], children: Callable[[Any], Iterable], root: Any
) -> Generator:
    """Generator for nodes in an arbitrary tree structure.

    is_branch: function of one arg, True if that arg represents a branch with children
    children: given an object for which is_branch returns true, return an iterator over the children
    root: Root of the collection
    """
    # let's do this with iteration rather than recursion
    nodes = deque([root])
    while len(nodes) > 0:
        this_node = nodes.popleft()
        yield this_node
        if is_branch(this_node):
            nodes.extendleft(reversed(list(children(this_node))))


def depth_search(pred: Callable[[Any], bool], collection):
    return filter(pred, tree_seq(is_seq, seq, collection))


T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


def reduce_kv(f: Callable[[T, U, V], T], init: T, coll: Mapping):
    """Reduces an associative collection; returns the result of
    applying f to init, the first key, and first value in coll,
    then applying f to that result and the second k,v etc.

    If coll contains no entries, returns init (f is not called)

    This version is not presently supported on vectors.
    """
    if len(coll) == 0:
        return init
    else:
        f2 = lambda accum, item: f(accum, item[0], item[1])
        return reduce(f2, coll.items(), init)


# from https://gist.github.com/SegFaultAX/10941721,
# and my isn't it elegant
def identity(e):
    return e


def walk(inner, outer, coll):
    """Oh wow.  Easiest just to look at
    https://clojuredocs.org/clojure.walk/postwalk
    """
    if isinstance(coll, list):
        return outer([inner(e) for e in coll])
    elif isinstance(coll, dict):
        return outer(dict([inner(e) for e in coll.items()]))
    elif isinstance(coll, tuple):
        return outer([inner(e) for e in coll])
    else:
        return outer(coll)


def postwalk(fn, coll):
    return walk(partial(postwalk, fn), fn, coll)
