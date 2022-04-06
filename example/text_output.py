from pprint import pformat

from interfaces import Output


class TextOutput(Output):
    def format_output(self, d: dict) -> str:
        return pformat(d)
