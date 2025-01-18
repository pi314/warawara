===============================================================================
``warawara.colors``
===============================================================================

This document describes the API set provided by ``warawara.colors``.

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


``Color``
-----------------------------------------------------------------------------
An abstract base class that is inherited by other Color types.

Intend to be used for type checking, like ``isinstance(obj, Color)``.

Two ``Color`` objects are defined equal if their escape sequence are equal.


``Color256``
-----------------------------------------------------------------------------
Represents a xterm 256 color.

The actual color displayed in your terminal might look different
depends on your palette settings.

.. code:: python

   c = color(214) # orange
   assert c.index == 214
   assert int(c) == 214
   assert str(c) == '\033[38;5;214m'
   assert c('text') == str(c) + 'text' + '\033[m'
   assert '{}{}{}'.format(c, 'text', nocolor) == c('text')

A Color256 object could be casted into a ColorRGB object or a ColorHSV object:

.. code:: python

   assert c.to_rgb() == ColorRGB(255, 175, 0)
   assert c.to_hsv() == ColorHSV(41, 100, 100)


``ColorRGB``
-----------------------------------------------------------------------------
Represents a RGB color.

.. code:: python

   c = ColorRGB(255, 175, 0) # orange
   assert c.r == 255
   assert c.g == 175
   assert c.b == 0
   assert c.rgb = (c.r, c.g, r.v)
   assert int(c) == 0xFFAF00
   assert str(c) == '\033[38;2;255;175;0m'
   assert c('text') == str(c) + 'text' + '\033[m'
   assert '{}{}{}'.format(c, 'text', nocolor) == c('text')

ColorRGB objects could be mixed to produce new colors:

.. code:: python

   red = ColorRGB('#FF0000')
   green = ColorRGB('#00FF00')
   assert red + green == ColorRGB('#FFFF00')
   assert (red + green) // 2 == ColorRGB('#7F7F00')
   assert ((red * 2) + green) // 2 == ColorRGB('#FF7F00')

A ColorRGB object could be casted into a ColorHSV object:

.. code:: python

   assert ColorRGB(255, 0, 0).to_rgb() == ColorRGB(255, 0, 0)
   assert ColorRGB(255, 0, 0).to_hsv() == ColorHSV(0, 100, 100)

Two sets of RGB values are provided, lowercase ``rgb`` for real values,
and uppercase ``RGB`` for regulated values that are
``round()`` and ``clamp()`` to ``range(0, 256)``.

.. code:: python

   c = ColorRGB(255, 174.5, 0) # nearly orange
   assert c.rgb == (255, 174.5, 0) # lowercase = real values
   assert c.RGB == (255, 174, 0)   # uppercase = regulated values


``ColorHSV``
-----------------------------------------------------------------------------
Represents a HSV color.

.. code:: python

   c = ColorHSV(41, 100, 100) # orange
   assert c.h == 41
   assert c.s == 100
   assert c.v == 100
   assert c.hsv == (c.h, c.s, c.v)
   assert int(c) == 41100100
   assert str(c) == '\033[38;2;255;174;0m'
   assert c('text') == str(c) + 'text' + '\033[m'
   assert '{}{}{}'.format(c, 'text', nocolor) == c('text')

A ColorHSV object could be casted into a ColorRGB object:

.. code:: python

   assert ColorHSV(41, 100, 100).to_rgb() == ColorRGB(255, 174, 0)
   assert ColorHSV(41, 100, 100).to_hsv() == ColorHSV(41, 100, 100)

Two sets of HSV values are provided, lowercase ``hsv`` for real values,
and uppercase ``HSV`` for regulated values that are
``round()`` and ``clamp()`` to proper range.

.. code:: python

   c = ColorHSV(21.5, 100, 100) # similar to clementine
   cc = c * 2 # an impossible color
   assert cc.hsv == (43, 200, 200)  # lowercase = real values
   assert cc.HSV == (43, 100, 100)  # uppercase = regulated values



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


``decolor()``
-----------------------------------------------------------------------------
Removes color sequences from input string.

.. code:: python

   s = 'some string'
   cs = color(214)('some string') # '\e[38;5;214msome string\e[m'
   assert decolor(cs) == s


``names``
-----------------------------------------------------------------------------
A list of named colors, that are pre-defined by warawara and could be accessed
with ``warawara.<color name>``.

The list was taken from `W3C CSS Color Module Level 3, 4.3. Extended color keywords`__,
with a few extensions.

Note that all these colors are mapped to the nearest xterm 256 color.
Their RGB value are likely not the consistent with W3C's definition.

.. _w3c_color_list: https://www.w3.org/TR/css-color-3/#svg-color
__ w3c_color_list_

* ``aliceblue``
* ``antiquewhite``
* ``aqua``
* ``aquamarine``
* ``azure``
* ``beige``
* ``bisque``
* ``black``
* ``blanchedalmond``
* ``blue``
* ``blueviolet``
* ``brown``
* ``burlywood``
* ``cadetblue``
* ``chartreuse``
* ``chocolate``
* ``clementine``
* ``coral``
* ``cornflowerblue``
* ``cornsilk``
* ``crimson``
* ``cyan``
* ``darkblue``
* ``darkcyan``
* ``darkgoldenrod``
* ``darkgray`` / ``darkgrey``
* ``darkgreen``
* ``darkkhaki``
* ``darkmagenta``
* ``darkolivegreen``
* ``darkorange``
* ``darkorchid``
* ``darkred``
* ``darksalmon``
* ``darkseagreen``
* ``darkslateblue``
* ``darkslategray`` / ``darkslategrey``
* ``darkturquoise``
* ``darkviolet``
* ``deeppink``
* ``deepskyblue``
* ``dimgray`` / ``dimgrey``
* ``dodgerblue``
* ``firebrick``
* ``floralwhite``
* ``forestgreen``
* ``fuchsia``
* ``gainsboro``
* ``ghostwhite``
* ``gold``
* ``goldenrod``
* ``gray`` / ``grey``
* ``green``
* ``greenyellow``
* ``honeydew``
* ``hotpink``
* ``indianred``
* ``indigo``
* ``ivory``
* ``khaki``
* ``lavender``
* ``lavenderblush``
* ``lawngreen``
* ``lemonchiffon``
* ``lightblue``
* ``lightcoral``
* ``lightcyan``
* ``lightgoldenrodyellow``
* ``lightgray`` / ``lightgrey``
* ``lightgreen``
* ``lightpink``
* ``lightsalmon``
* ``lightseagreen``
* ``lightskyblue``
* ``lightslategray`` / ``lightslategrey``
* ``lightsteelblue``
* ``lightyellow``
* ``lime``
* ``limegreen``
* ``linen``
* ``magenta``
* ``maroon``
* ``mediumaquamarine``
* ``mediumblue``
* ``mediumorchid``
* ``mediumpurple``
* ``mediumseagreen``
* ``mediumslateblue``
* ``mediumspringgreen``
* ``mediumturquoise``
* ``mediumvioletred``
* ``midnightblue``
* ``mintcream``
* ``mistyrose``
* ``moccasin``
* ``murasaki``
* ``navajowhite``
* ``navy``
* ``oldlace``
* ``olive``
* ``olivedrab``
* ``orange``
* ``orangered``
* ``orchid``
* ``palegoldenrod``
* ``palegreen``
* ``paleturquoise``
* ``palevioletred``
* ``papayawhip``
* ``peachpuff``
* ``peru``
* ``pink``
* ``plum``
* ``powderblue``
* ``purple``
* ``red``
* ``rosybrown``
* ``royalblue``
* ``saddlebrown``
* ``salmon``
* ``sandybrown``
* ``seagreen``
* ``seashell``
* ``sienna``
* ``silver``
* ``skyblue``
* ``slateblue``
* ``slategray`` / ``slategrey``
* ``snow``
* ``springgreen``
* ``steelblue``
* ``tan``
* ``teal``
* ``thistle``
* ``tomato``
* ``turquoise``
* ``violet``
* ``wheat``
* ``white``
* ``whitesmoke``
* ``yellow``
* ``yellowgreen``


``nocolor``
-----------------------------------------------------------------------------
A special color name that has the following properties:

.. code:: python

   assert nocolor == color()
   assert str(nocolor) == '\033[m'
   assert '{}'.format(nocolor) == '\033[m'
   assert nocolor('anything') == 'anything'


``gradient()``
-----------------------------------------------------------------------------
Produces a series of colors from ``A`` to ``B`` of length ``N >= 2``.

.. code:: python

   g = gradient(A, B, N) # [A, ..., B]

If ``A`` and ``B`` are different Color types, ``(A, B)`` is returned.

For Color256 colors, the gradient is calculated on xterm 256 color cube.
RGB range (``range(16, 232)``) and Grayscale range (``range(232,256)``)
are defined as not compatible to each other.

Keyword argument ``reverse=True`` could be specified to reverse the result.

For ColorHSV colors, keyword argument ``clockwise=True`` / ``clockwise=False``
could be specified to force the gradient sequence to be clockwise or counter-clockwise.
If not specified, a shorter gradient sequence is preferred.
