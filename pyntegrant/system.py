"""Functions that have more to do with building and manipulating systems
"""
from typing import Any, Callable, Optional

from pyntegrant.initializer import Initializer
from pyntegrant.loaders import default_ref_selector, default_ref_transform, replace_refs
from pyntegrant.map import Key, Keyset, SystemMap, build, dependent_keys


class System(object):
    """A system of components, initialized from a config."""

    def __init__(self, built_config: SystemMap, original_config: SystemMap):
        self.__dict__.update(**built_config)
        self._original_config = original_config

    @classmethod
    def from_config(
        cls,
        config: SystemMap,
        initializer: Initializer,
        keys: Optional[Keyset] = None,
        ref_selector: Callable[[Any], bool] = default_ref_selector,
        transform: Callable[[Any], bool] = default_ref_transform,
    ):
        """Creates a system given a config and an initializer.

        This is the entry point to creating a system from a configuration.
        The config must be in Python dict format (in other words, using `PRef`
        references, not text-based "#p/ref ..." references); you can replace
        "#p/ref ..." references with `PRef` references with `replace_refs`
        """
        original_config = replace_refs(config)
        keys = (
            config.keys() if keys is None else frozenset(dependent_keys(config, keys))
        )
        built_config = build(original_config, keys, initializer.initialize)
        return cls(built_config, original_config)
