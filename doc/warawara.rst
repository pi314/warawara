===============================================================================
``warawara``
===============================================================================

This is the index document of package ``warawara``.

.. contents:: Table of Contents


Installation
-----------------------------------------------------------------------------

.. code:: shell

   $ pip3 install warawara


Or just copy the whole folder to your machine, and add the path to ``sys.path``:

.. code:: python

   import sys
   sys.path.insert(0, '/some/path/to/place/warawara')
   import warawara


Test
-----------------------------------------------------------------------------

Testing:

.. code:: shell

   $ python3 -m unittest

With `pytest-cov <https://pytest-cov.readthedocs.io/en/latest/>`_:

.. code:: shell

   $ pipx install pytest-cov --include-deps
   # or
   $ pipx install pytest
   $ pipx runpip pytest install pytest-cov

   $ pytest --cov=warawara --cov-report=html


"Attributes"
-----------------------------------------------------------------------------

Like Python standard libraries, ``warawara`` divide its functionalities into
different categories.

For example, ``warawara.subproc`` contains functions about sub-processes,
``warawara.colors`` contains fucntions about colors.

(They are not sub-modules, so they are not ``from warawara import xxx`` able.)

For convenience, if not specified, functions are accessible directly at package level.
In other words, ``warawara.subproc.xxx`` is shortcut to ``warawara.xxx``.

Documents and descriptions of the categories are as following:

* `warawara <warawara.rst>`_
* `warawara.colors <warawara.colors.rst>`_
* ``warawara.fs`` (WIP)
* ``warawara.itertools`` (WIP)
* `warawara.math <warawara.math.rst>_`
* ``warawara.regex`` (WIP)
* `warawara.sh <warawara.sh.rst>`_
* ``warawara.subproc`` (WIP)
* ``warawara.tui`` (WIP)
