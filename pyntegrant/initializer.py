"""Initializer for single-dispatch
"""
from typing import Callable, Mapping

from icontract import require


class Initializer(object):
    """The Initializer class represents a single-dispatch function where
    the dispatch is based on keys in the configuration.  Each key in the config
    should have an entry in the initializer which is responsible for creating
    the system object which corresponds to that key.
    """

    def __init__(self):
        self.handlers = {}
        self.default_handler = None

    def register_default(self):
        """Registers a default handler.  Fails if attempted twice.
        The default handler must take a single argument (rather
        than other handlers which can take multiple keyword arguments
        and be initialized that way via a dict)
        """

        def register_function(f):
            assert self.default_handler is None
            self.default_handler = f
            return f

        return register_function

    def register(self, key: str):
        """Decorator to register handlers for the initializer.

        One would create an initializer (`result=Initializer`) and
        then register a number of handlers, where each registration
        corresponds to a key in the config (`@result.register("server")`)
        """

        def register_function(f):
            self.handlers[key] = f
            return f

        return register_function

    def initialize(self, key, value):
        """Dispatches initialization based on `key`.

        If the value is a mapping, calls the handler with `**value`
        so that handlers can have keyword arguments and values can be
        dicts.  If the value is a single non-mapping value, it is passed
        to the handler as a single argument.
        """
        if key in self.handlers:
            if isinstance(value, Mapping):
                return self.handlers[key](**value)
            else:
                return self.handlers[key](value)
        elif self.default_handler is not None:
            return self.default_handler(value)
        else:
            raise ValueError(f"No handler found for key {key}")
