README
======


**NAME**


``OBR`` - object runtime


**SYNOPSIS**

::

    >>> from obr.object import *
    >>> o = Object()
    >>> o.a = "b"
    >>> str(loads(dumps(o)))
    "{'a': 'b'}"


**DESCRIPTION**


``OBR`` contains all the python3 code to program objects in a functional
way. It provides a base Object class that has only dunder methods, all
methods are factored out into functions with the objects as the first
argument. It is called Object Programming (OP), OOP without the
oriented.

``OBR`` allows for easy json save//load to/from disk of objects. It
provides an "clean namespace" Object class that only has dunder
methods, so the namespace is not cluttered with method names. This
makes storing and reading to/from json possible.


``OBR`` has all you need to program a unix cli program, such as disk
perisistence for configuration files, event handler to handle the
client/server connection, deferred exception handling to not crash
on an error, etc.


**INSTALL**

::

    $ pipx install obr
    $ pipx ensurepath


**SOURCE**


source is at https://github.com/bthate/obr


**AUTHOR**


Bart Thate <bthate@dds.nl>


**COPYRIGHT**


``OBR`` is Public Domain.
