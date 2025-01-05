===============================================================================
``warawara``
===============================================================================

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

(They are not sub-modules, so they are not ``from warawara import`` able.)

Documents and descriptions of the categories are as following:

* ``warawara.rst`` (this document)
* `warawara_colors.rst <warawara_colors.rst>`_
