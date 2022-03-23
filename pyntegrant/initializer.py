"""Initializer for single-dispatch
"""
from typing import Callable, Mapping


class Initializer(object):
    def __init__(self):
        self.handlers = {}

    def register(self, key: str):
        def register_function(f):
            self.handlers[key] = f
            return f

        return register_function

    def initialize(self, key, value):
        if isinstance(value, Mapping):
            return self.handlers[key](**value)
        else:
            return self.handlers[key](value)
