===============================================================================
``warawara.itertools``
===============================================================================

This document describes the API set provided by ``warawara.itertools``.

For the index of this package, see `warawara.rst <warawara.rst>`_.

.. contents:: Table of Contents


``is_iterable(obj)``
-----------------------------------------------------------------------------
Returns ``True`` if ``obj`` is iterable and ``False`` otherwise.


``unwrap(obj=None)``
-----------------------------------------------------------------------------
Try to unpack ``obj`` as much as possible.

``str`` stay as-is and doesn't unpacked to characters.

.. code:: python

   assert unpack([[[1, 2, 3]]]) is [1, 2, 3]
   assert unpack([[True]]) is True
   assert unpack('warawara') is 'warawara'


``flatten(tree)``
-----------------------------------------------------------------------------
Flattens every nested list/tuple and merge them into one.

.. code:: python

   assert flatten([[1, 2, 3], [4, 5, 6], [7], [8, 9]]) == [1, 2, 3, 4, 5, 6, 7, 8, 9]


``lookahead(iterable)``
-----------------------------------------------------------------------------
Returns a generator object that generate boolean values to indicate the last element.

Simioart to ``enumerate()`` that creates ``index`` values for ``elem``,
``lookahead()`` creates ``is_last`` for ``elem``.

.. code:: python

   data = []
   for val, is_last in lookahead([1, 2, 3, 4, 5]):
       data.append((val, is_last))

   assert data == [
       (1, False),
       (2, False),
       (3, False),
       (4, False),
       (5, True),
       ]


``zip_longest(*iterables, fillvalues=None)``
-----------------------------------------------------------------------------
Similar to standard ``itertools.zip_longest()``, but warawara version supports
setting ``fillvalue`` for each sequences.

.. code:: python

   A = list(zip_longest('ABCD', [1, 2], fillvalues=('#', 0))),
   B = [
       ('A', 1),
       ('B', 2),
       ('C', 0),
       ('D', 0),
       ]
   assert A == B

   A = list(zip_longest('AB', [1, 2, 3, 4], fillvalues=('#', 0))),
   B = [
       ('A', 1),
       ('B', 2),
       ('#', 3),
       ('#', 4),
       ]
   assert A == B
