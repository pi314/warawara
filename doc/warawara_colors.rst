===============================================================================
``warawara.colors``
===============================================================================

This document describes the functionality of ``warawara.colors``.

For the index of this package, see `warawara.rst <warawara.rst>`_.

.. contents:: Table of Contents


``color()``
-----------------------------------------------------------------------------
A factory function that produces color objects based on input arguments.

.. code:: python

   color()     # returns a Color256() object that does nothing
   color(214)  # color 214 in 256 colors, which is darkorange
   color(255, 175, 0)  # by RGB values
   color('#FFAF00')    # by RGB hex representation
   color('@41,100,100')  # by HSV value

An object of the following types would be returned based on input arguments:

* `Color256`_
* `ColorRGB`_
* `ColorHSV`_

If the argument does not have correct format, ``TypeError`` is raised.


``Color256``
-----------------------------------------------------------------------------
Represents a VT100 256 color.

The actual color displayed in your terminal might look different
depends on your palette settings.

.. code:: python

   c = color(214) # orange
   assert c.index == 214
   assert int(c) == 214
   assert c('text') == '\033[38;5;214mtext\033[m'

A Color256 object could be casted into a ColorRGB object:

.. code:: python

   assert c.to_rgb() == ColorRGB(255, 175, 0)


``ColorRGB``
-----------------------------------------------------------------------------
Represents a RGB color.

.. code:: python

   c = ColorRGB(255, 175, 0) # orange
   assert c.r == 255
   assert c.g == 175
   assert c.b == 0
   assert c.rgb = (255, 175, 0)
   assert c('text') == '\033[38;2;255;175;0mtext\033[m'

ColorRGB objects could be mixed to produce new colors:

.. code:: python

   red = ColorRGB('#FF0000')
   green = ColorRGB('#00FF00')
   assert red + green == ColorRGB('#FFFF00')
   assert (red + green) // 2 == ColorRGB('#7F7F00')
   assert ((red * 2) + green) // 2 == ColorRGB('#FF7F00')

A Color256 object could be casted into a ColorHSV object:

.. code:: python

   assert ColorRGB(255, 0, 0).to_hsv() == ColorHSV(0, 100, 100)


``ColorHSV``
-----------------------------------------------------------------------------
Represents a HSV color.

.. code:: python

   c = ColorHSV(41, 100, 100) # orange
   assert c.h == 41
   assert c.s == 100
   assert c.v == 100
   assert c('text') == '\033[38;2;255;175;0mtext\033[m'


``decolor()``
-----------------------------------------------------------------------------
Removes color sequence from input string.

.. code:: python

   s = 'some string'
   cs = color(214)('some string') # '\e[38;5;214msome string\e[m'
   decolor(s) # 'some string'


``gradient()``
-----------------------------------------------------------------------------
Produces a series of colors from ``A`` to ``B`` of length ``N``.

.. code:: python

   g = gradient(A, B, N) # [A, ..., B]

``A`` and ``B`` must be in the same Color type,
the return value is also in the same Color type.

For Color256 colors, the gradient is calculated on VT100 256 color cube.
Grayscale range (``range(232,256)``) and RGB range (``range(16, 232)``) are separated.


``Color``
-----------------------------------------------------------------------------
An abstract base class that is inherited by other Color types.

Intend to be used for type checking, like ``isinstance(obj, Color)``.


``ColorCompound``
-----------------------------------------------------------------------------
Binds two Color object together, one for foreground and one for background.

.. code:: python

   orange = Color256(208)
   darkorange = ColorRGB(255, 175, 0)

   # Becomes background
   assert (~orange)('ORANGE') == '\033[48;5;208mORANGE\033[m'

   # Foreground and background
   od = orange / darkorange
   assert od('ORANGE') == '\033[38;5;208;48;2;255;175;0mORANGE\033[m\n'

In addition, ColorCompound objects supports ``__or__`` operation.
Foreground remains foreground, background remains background,
and the later color overrides the former:

.. code:: python

   ry = red / yellow
   ig = ~green
   ryig = ry | ig
   assert ryig == red / green
   assert ryig('text') == '\033[38;5;9;48;5;12mtext\033[m'
