"""Functions that have more to do with building and manipulating systems
"""
from typing import Any, Callable, Optional

from pyntegrant.initializer import Initializer
from pyntegrant.loaders import default_ref_selector, default_ref_transform, replace_refs
from pyntegrant.map import Key, Keyset, SystemMap, build


class System(object):
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
        original_config = replace_refs(config)
        keys = config.keys() if keys is None else keys
        built_config = build(original_config, keys, initializer.initialize)
        return cls(built_config, original_config)
