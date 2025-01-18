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


``clamp(min, x, max)``
-----------------------------------------------------------------------------
Clamps the value into the specified interval.

* If ``x`` is less than ``min``, ``min`` is returned
* If ``x`` is greater than ``max``, ``max`` is returned
* Otherwise, ``x`` is returned
