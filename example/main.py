from counter_processor import CounterProcessor
from string_input import StringInput
from text_analyzer import TextAnalyzer
from text_output import TextOutput

from pyntegrant.initializer import Initializer
from pyntegrant.map import PRef
from pyntegrant.system import System


def initializer() -> Initializer:

    result = Initializer()

    @result.register("input")
    def _(classname, input):
        if classname == "StringInput":
            return StringInput(input=input)
        else:
            assert False

    @result.register("output")
    def _(classname):
        if classname == "TextOutput":
            return TextOutput()
        else:
            assert False

    @result.register("processor")
    def _(classname):
        if classname == "CounterProcessor":
            return CounterProcessor()
        else:
            assert False

    @result.register("analyzer")
    def _(input, output, processor):
        return TextAnalyzer(input, processor, output)

    return result


if __name__ == "__main__":

    config = {
        "input": dict(classname="StringInput", input="able was I ere I saw elba"),
        "output": dict(classname="TextOutput"),
        "processor": dict(classname="CounterProcessor"),
        "analyzer": dict(
            input=PRef("input"), output=PRef("output"), processor=PRef("processor")
        ),
    }

    system = System.from_config(config, initializer())
    print(system.analyzer.process())
