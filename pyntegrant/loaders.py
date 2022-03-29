"""Structures and functions for loading a configuration from storage,
typically in the form of loading from storage into a dict with string
refs, and processing that dict to use PRef refs for processing as a
SystemMap
"""
import json
from typing import Any, Callable

import toml
from icontract import require
from pyrsistent import pmap

from pyntegrant.helpers import postwalk
from pyntegrant.map import PRef, SystemMap


def default_ref_selector(x: Any) -> bool:
    """The default "reference" form selector, which finds elements
    which are strings beginning with "#p/ref"
    """
    return isinstance(x, str) and x.startswith("#p/ref")


@require(lambda x: default_ref_selector(x) == True)
def default_ref_transform(x: Any) -> Any:
    """The default transformation, transforming eg
    "#p/ref key" into PRef(key='key')
    """
    return PRef(key=x[7:])


def replace_refs(
    config: SystemMap,
    selector: Callable[[Any], bool] = default_ref_selector,
    transform: Callable[[Any], Any] = default_ref_transform,
) -> SystemMap:
    """In the given SystemMap dict, replace all strings
    representing a ref (in the format "#ref name")
    """
    return pmap(postwalk(lambda x: transform(x) if selector(x) else x, config))


def from_dict(d: SystemMap) -> SystemMap:
    """Create a PRef-style map from a dict with string refs"""
    return replace_refs(d)


def from_toml(toml_path: str) -> SystemMap:
    """Create a PRef-style map from a toml file"""
    return from_dict(toml.load(toml_path))


def from_tomls(toml_string: str) -> SystemMap:
    """Create a PRef-style map from toml string"""
    return from_dict(toml.loads(toml_string))


def from_json(json_path: str) -> SystemMap:
    """Create a PRef-style map from json file"""
    with open(json_path, "r") as f:
        return from_dict(json.load(f))


def from_jsons(json_str: str) -> SystemMap:
    """Create a PRef-style map from json string"""
    return from_dict(json.loads(json_str))
