===============================================================================
``warawara.colors``
===============================================================================

.. contents:: Table of Contents


``color()``
-----------------------------------------------------------------------------
A factory function that produces color objects based on input arguments.

.. code:: python

  color()     # returns a Color256() object that does nothing
  color(214)  # color 214 in 256 colors, which is darkorange
  color(255, 175, 0)  # construct by RGB values
  color('#FFAF00')    # construct by RGB hex representation
  color('@41,100,100')  # construct by HSV value

The different classes are used to construct color objects:

* ``Color256``
* ``ColorRGB``
* ``ColorHSV``


``Color``
-----------------------------------------------------------------------------
An abstract base class that inherit by other Color classes.

Intend to be used like ``isinstance(obj, Color)``.


``Color256``
-----------------------------------------------------------------------------
Represents the VT100 256 color space.

.. code:: python

  c = color(214) # get color 214

  assert c.index == 214
  assert c('text') == '\033[38;5;214mtext\033[m'

Note that applying it to an already colored string could cause strange affects.


``ColorRGB``
-----------------------------------------------------------------------------
Represents the RGB color space

.. code:: python

  c = color(255, 175, 0) # dark orange

  assert c.r == 255
  assert c.g == 175
  assert c.b == 0
  assert c('text') == '\033[38;2;255;175;0mtext\033[m'

Note that applying it to an already colored string could cause strange affects.


``ColorHSV``
-----------------------------------------------------------------------------


``decolor``
-----------------------------------------------------------------------------
A funciton that removes color sequence from input string.

.. code:: python

  s = 'some string'
  cs = color(214)('some string') # '\e[38;5;214msome string\e[m'
  decolor(s) # 'some string'


``gradient()``
-----------------------------------------------------------------------------
Produce a series of colors of length ``N``
that is the gradient of given ``A``, ``B``, colors.

.. code:: python

  gradient(A, B, N)
