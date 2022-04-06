.. Pyntegrant documentation master file, created by
   sphinx-quickstart on Sun Apr  3 12:13:01 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==========================================================
 Pyntegrant: a Pynt-sized version of Integrant for Python
==========================================================

The good old SOLID principles beloved by more statically-typed OO
languages are often decried by Python folks.  That's too bad, because
they still apply--and one in particular (dependency inversion, or
"inversion of control") can actually lead to excellent separation of
concerns and rapid application development by encouraging software
modules to be truly independent of each other.

As Robert Martin would say:

    "High level modules should not depend on low-level modules.  Both
    should depend on abstractions.  Abstractions should not depend on
    details.  Details should depend on abstractions."

The idea here is that applications should be constructed as systems of
modules, where each module only communicates through other modules via
a defined interface.

Some would argue that Python's duck-typing makes the "defined
interface" unnecessary--I would argue that while that's true, that
just makes this approach *even more powerful!*

What that also means is that you need a way to *assemble* these
systems of modules that is completely separate of the modules
themselves.  And that's where Pyntegrant comes in.  Looking at the
existing "dependency injection" modules available in other languages,
I was struck by the elegance of James Reeves' `Integrant
<https://github.com/weavejester/integrant>`_ microframework enough
that I felt it worth porting a subset of its functionality to Python.
A one-day personal hackathon convinced me of its value in allowing
parts of an application to vary independently such that they could be
remixed easily and effectively.

In "The Mythical Man-Month", Fred Brooks wrote

    "Build one to throw away.  You will, anyhow."

but what if you made it easy to throw *lots* of them away?


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   example

.. toctree::
   :maxdepth: 2
   :caption: API:

   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
