===============================================================================
``warawara.math``
===============================================================================

This document describes the API set provided by ``warawara.math``.

For the index of this package, see `warawara.rst <warawara.rst>`_.

.. contents:: Table of Contents


``is_uint8(i)``
-----------------------------------------------------------------------------
Checks if the argument ``i`` is a 8-bit unsigned integer.

Returns ``True`` if ``i`` fulfills all of the following condition:

* ``isinstance(i, int)``
* ``not isinstance(i, bool)``
* ``0 <= i < 256``


``sgn(i)``
-----------------------------------------------------------------------------
Return the sign of parameter ``i``.

* ``-1`` if ``i < 0``
* ``1`` if ``i > 0``
* ``0`` otherwise


``lerp(a, b, t)``
-----------------------------------------------------------------------------
Calculates the linear interpolation or extrapolation of argument ``a``, ``b`` at ratio ``t``.

* If ``t = 0``, ``a`` is returned
* If ``t = 1``, ``b`` is returned
* If ``0 < t < 1``, the linear interpolation is returned
* Otherwise, the linear extrapolation is returned

``lerp()`` supports ``vector`` type described below.


``clamp(min, x, max)``
-----------------------------------------------------------------------------
Clamps the value into the specified interval.

* If ``x`` is less than ``min``, ``min`` is returned
* If ``x`` is greater than ``max``, ``max`` is returned
* Otherwise, ``x`` is returned


class ``vector(*args)``
-----------------------------------------------------------------------------
A ``tuple``-like object that represents vector of mathematical meaning.

.. code:: python

   v1 = vector(1, 2, 3)
   v2 = vector(4, 5, 6)
   assert v1 + v2 == (5, 7, 9)
   assert v1 - v2 == (-3, -3, -3)

   assert v1 + 2 == (3, 4, 5)
   assert 2 + v1 == (3, 4, 5)

   assert v1 - 2 == (-1, 0, 1)

   assert v1 * 2 == (2, 4, 6)
   assert 2 * v1 == (2, 4, 6)

   assert (v1 / 2, (0.5, 1.0, 1.5))
   assert (v1 // 2, (0, 1, 1))

   assert v1.map(lambda x: x * 10) == (10, 20, 30)


``interval(a, b, close=True)``
-----------------------------------------------------------------------------
Returns a ``List[int]`` that starts from ``a`` and ends with ``b``.

If ``close=False``, ``a`` and ``b`` are excluded from the result.

.. code:: python

   assert interval(3, 1) == [3, 2, 1]
   assert interval(3, -3) == [3, 2, 1, 0, -1, -2, -3]
   assert interval(3, -3, close=False) == [2, 1, 0, -1, -2]

   assert interval(3, 3) == [3]
   assert interval(3, 3, close=False) == []


``distribute(samples, N)``
-----------------------------------------------------------------------------
Returns a list that "distrubutes" ``samples`` to ``N`` items.

* If ``N`` is larger than ``len(samples)``, some items are repeated in the result
* If ``N`` is less than ``len(samples)``, some items are dropped from the result

.. code:: python

   samples = (1, 2, 3, 4, 5)
   assert distribute(samples, 5) == samples
   assert distribute(samples, 3) == (1, 3, 5)
   assert distribute(samples, 10) == (1, 1, 2, 2, 3, 3, 4, 4, 5, 5)
