Extended Example
================

Pyntegrant really shines when used to construct fairly complex systems
("the CLI depends on a task manager and a database; the task manager
could be local or remote; the database could be file-based,
document-based, or networked; the networked database depends on a host
and port..."), but fairly complex applications are harder to
demonstrate, so this is of necessity a pretty darn trivial example.

Suppose we wanted to make a simple system that
* took in data and presented it as a string
* performed some analysis on that string (character counts for example)
* presented the output as a formatted string

we can represent those parts of the system as abstract base classes
(you could also use protocols, and strictly speaking this part isn't even
necessary but it helps):

.. code-block:: python

    from abc import ABC, abstractmethod

    class Input(ABC):

	@abstractmethod
	def get_input(self)->str:
	    ...

    class Processor(ABC):

	@abstractmethod
	def process_input(self, s: str)->dict:
	    ...

    class Output(ABC):

	@abstractmethod
	def format_output(self, d: dict)->str:
	    ...

and then have an analysis class that uses these interfaces:

.. code-block:: python

    class TextAnalyzer:

	def __init__(self, input: Input, processor: Processor, output: Output):
	    self.input = input
	    self.processor = processor
	    self.output = output

	def process(self):
	    return self.output.format_output(self.processor.process_input(self.input.get_input()))

Note that the ``TextAnalyzer`` can happily use *any* implementation of
the above classes without knowing anything at all about them.  So
we're free to implement any version of the above interfaces, and we will:

.. code-block:: python

    class StringInput(Input):

	def __init__(self, input: str):

	    self.s = input

	def get_input(self)->str:
	    return self.s

    from collections import Counter
    class CounterProcessor(Processor):

	def process_input(self, s: str)->dict:
	    c = Counter(s)
	    total_chars = len(s)
	    distinct_chars = len(c)

	    return dict(total_chars=total_chars, distinct_chars=distinct_chars, character_count=c)

    from pprint import pformat
    class TextOutput(Output):

	def format_output(self, d: dict)->str:
	    return pformat(d)

Each of the above is in its own module; our base ``TextAnalyzer`` knows nothing at all about
these, even their names.  It's up to a configuration to put it all together.

That configuration looks something like this:

.. code-block:: python

    config = {
        "input": dict(classname="StringInput", input="able was I ere I saw elba"),
        "output": dict(classname="TextOutput"),
        "processor": dict(classname="CounterProcessor"),
        "analyzer": dict(
            input=PRef("input"), output=PRef("output"), processor=PRef("processor")
        ),
    }

This is in python ``dict`` format for clarity, but it could be
presented in other formats such as JSON or (very usefully) TOML, where
values such as ``PRef("input")`` are represented as strings of the
form "#p/ref input", making configurations pure-data.  The keys in the
dictionary correspond to objects in the completed systsem; the values
represent arguments which will be passed to an ``Initializer``.

Of note are the ``PRef`` objects in the ``analyzer`` values.  These
represent Pyntegrant *references* which are initialized in reverse
dependency order.

When this system is constructed, Pyntagrant sees that it can't create
the ``analyzer`` until it has created the ``input``, ``output``, and
``processor`` references, so it creates them and then substitutes
their *created values* into the arguments to ``analyzer``.

The system can then be configured and used as:

.. code-block:: python

    system = System.from_config(config, initializer())
    print(system.analyzer.process())

And the system will be created in the right order, the analyzer will
be created with completely opaque dependencies, and the system will
run, displaying::

  {'character_count': Counter({' ': 6,
                             'a': 4,
                             'e': 4,
                             'b': 2,
                             'l': 2,
                             'w': 2,
                             's': 2,
                             'I': 2,
                             'r': 1}),
 'distinct_chars': 9,
 'total_chars': 25}

The Initializer
---------------

The heavy lifting of object construction is the ``Initializer`` object
which acts as a single-dispatch function.  In this case, our
initializer is built by a function which creates an Initializer and
registers one handler for every possible base key.  Those handlers are
passed the values in the configuration either as keyword arguments or
a ``**kwargs`` block.  Here, the first argument for several is a class
name which can be used to instantiate various classes as
substitutions, but this is not necessary; in the case of the analyzer,
only one type of object is created.

.. code-block:: python

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
