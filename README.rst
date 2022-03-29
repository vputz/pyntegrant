==========
Pyntegrant
==========

While IoC and dependency injection aren't as much of a thing in Python
as they are in many compiled languages, that doesn't mean they don't
have their place in decomposition of a complex architecture and
assembly of systems; there's something very nice about completely
separated modules that communicate based on shared abstractions which
are then assembled by a separate piece of code into running systems.

But despite the many microframeworks for dependency injection that
I've seen for Python, I haven't seen any that seem as elegant as the
`Integrant <https://github.com/weavejester/integrant>`_ microframework
enjoyed by Clojurists.  This is an effort to remedy that, but as I
haven't loads of time to invest in it, it's a pale shadow of the
original.

Still, shadows have power.  It can already do the initialization portion
of a system, although items like prep, halt, suspend, etc remain,
as do derived keys and refsets.  But one thing at a time.

As of the 0.1.0 prerelease, all that works is the basic assembly of a
system from a configuration (in Python, JSON, or TOML) and it's
surprising how effective that actually can be.  Unfortunately error
messages are lightly cryptic and documentation is nonexistent, but
more will be coming shortly.
