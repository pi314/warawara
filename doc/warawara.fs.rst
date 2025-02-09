===============================================================================
``warawara.fs``
===============================================================================

This document describes the API set provided by ``warawara.fs``.

For the index of this package, see `warawara.rst <warawara.rst>`_.

.. contents:: Table of Contents


``open(file, mode=None, rstrip='\r\n', newline='\n', **kwargs)``
-----------------------------------------------------------------------------
A factory function that:

* Sets default ``encoding`` to ``'utf-8'``, if not specified
* Sets default ``errors`` to ``'backslashreplace'``, if not specifed
* If ``mode`` does not contain ``'b'``, returns a wrapper object

The returned wrapper object relays method calls to the underlying file object,
in addition it provides the following methods for convenience:

* ``writeline(*args)``: writes ``' '.join(args) + newline`` into file
* ``writelines(lines)``: write each elements in ``lines`` into file
* ``readline()``: read a line from file, and ``rstrip`` newline characters
* ``readlines()`` and ``__iter__()``: read all lines from file

.. code:: python

   import warawara

   with warawara.open(path, 'w') as f:
       f.writelines(['a', 'b', 'c'])
       f.writeline('d')

   with warawara.open(path) as f:
       assert f.readlines() == ['a', 'b', 'c', 'd']


``natsorted(iterable, key=None)``
-----------------------------------------------------------------------------
A utility function that mimics the very basic functionality of `natsort <https://pypi.org/project/natsort/>`_

This function was made for sorting ``os.listdir()`` with a slightly better result.

.. code:: python

   assert wara.natsorted([
           'apple1',
           'apple10',
           'banana10',
           'apple2',
           'banana1',
           'banana3',
       ]) == [
           'apple1',
           'apple2',
           'apple10',
           'banana1',
           'banana3',
           'banana10',
       ]
