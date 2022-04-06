Quickstart
==========

Pyntegrant enables you to build a system through a *configuration* and an *initializer*.

Using a toy example (see the "extended example" for explanation) one can create a config:

.. code-block:: python

    config = {
        "input": dict(classname="StringInput", input="able was I ere I saw elba"),
        "output": dict(classname="TextOutput"),
        "processor": dict(classname="CounterProcessor"),
        "analyzer": dict(
            input=PRef("input"), output=PRef("output"), processor=PRef("processor")
        ),
    }

the configuration could be a python dict as above, or JSON, or even TOML:

.. code-block:: toml

    [input]
    classname="StringInput"
    input="able was I ere I saw elba"

    [output]
    classname="TextOutput"

    [processor]
    classname = "CounterProcessor"

    [analyzer]:
    input="#p/ref input"
    output="#p/ref output"
    processor="#p/ref processor"

which can be loaded with ``pyntegrant.loaders.from_toml`` or ``from_tomls``.

For each key in the config, one creates an entry in an initializer:

.. code-block:: python

    def initializer() -> Initializer:

	result = Initializer()

	@result.register("analyzer")
	def _(input, output, processor):
	    return TextAnalyzer(input, processor, output)

	...

and then the system can be built:

.. code-block:: python

    system = System.from_config(config, initializer())
    print(system.analyzer.process())

Pyntegrant will run through the configuration and create an object
with each key in reverse dependency order, with references created and
replaced as it goes.  In other words, in this simple config, it will
create an ``input`` object, an ``output`` object, and a ``processor``
object, and finally create the ``analyzer`` object with those three as
arguments.

In this way, each part of the system can vary independently with zero
knowledge of each others' existence--and since the configurations can
be pure data, it's possible to mix and match parts of the system via
pure-data inputs or reconfigure at a moment's notice.

Pyntegrant does not *yet* support Integrant's reverse-shutdown or
suspend functionality; I will add it as time and requirements allow.

Since the initializer can return anything, it's even possible to wrap
up part of the system in an external process and return a future from
``os.popen``--no need for docker-compose or kubernetes to start
building a microservice-based system!
