warawara.colors
===============================================================================

This document describes the API set provided by `warawara.colors`.

For the index of this package, see [warawara.md](warawara.md).


`color()`
-------------------------------------------------------------------------------

A factory function that produces color objects based on input arguments.

__Parameters__
```
color()
color(index)
color(R, G, B)
color('#RRGGBB')
color('@HHH,SSS,VVV')
```

__Examples__

```python
color()              # Color256: empty
color(214)           # Color256: darkorange
color(255, 175, 0)   # ColorRGB: orange
color('#FFAF00')     # ColorRGB: orange
color('@41,100,100') # ColorHSV: orange
```

If the argument does not have correct format, `TypeError` is raised.

See [Color256](#class-color256), [ColorRGB](#class-colorrgb),
and [ColorHSV](#class-colorhsv) for more details.


`class Color`
-------------------------------------------------------------------------------

An abstract base class that is inherited by other Color types.

It's intended to be used for type checking. For example, `isinstance(obj, Color)`.

Two `Color` objects are defined equal if their escape sequence are equal.


`class Color256`
-------------------------------------------------------------------------------

`class Color256(index)`

Represents a xterm 256 color.

The actual color displayed in your terminal might look different
depends on your palette settings.

```python
c = Color256(214) # orange
assert c.index == 214
assert int(c) == 214
assert str(c) == '\033[38;5;214m'
assert c('text') == str(c) + 'text' + '\033[m'
assert '{}{}{}'.format(c, 'text', nocolor) == c('text')
```

A `Color256` object could be casted into a `ColorRGB` object or a `ColorHSV`
object through `to_rgb()` or `to_hsv()` methods:

```python
assert c.to_rgb() == ColorRGB(255, 175, 0)
assert c.to_hsv() == ColorHSV(41, 100, 100)
```

class ``ColorRGB``
-----------------------------------------------------------------------------

Represents a RGB color.

__Parameters__
```
ColorRGB(R, G, B)
ColorRGB('#RRGGBB')
```

__Examples__
```python
c = ColorRGB(255, 175, 0) # orange
assert c.r == 255
assert c.g == 175
assert c.b == 0
assert c.rgb = (c.r, c.g, r.v)
assert int(c) == 0xFFAF00
assert str(c) == '\033[38;2;255;175;0m'
assert c('text') == str(c) + 'text' + '\033[m'
assert '{}{}{}'.format(c, 'text', nocolor) == c('text')
```

ColorRGB objects could be mixed to produce new colors:

```python
red = ColorRGB('#FF0000')
green = ColorRGB('#00FF00')
assert red + green == ColorRGB('#FFFF00')
assert (red + green) // 2 == ColorRGB('#7F7F00')
assert ((red * 2) + green) // 2 == ColorRGB('#FF7F00')
```

A ColorRGB object could be casted into a ColorHSV object:

```python
assert ColorRGB(255, 0, 0).to_rgb() == ColorRGB(255, 0, 0)
assert ColorRGB(255, 0, 0).to_hsv() == ColorHSV(0, 100, 100)
```

Two sets of RGB values are provided, lowercase ``rgb`` for real values,
and uppercase ``RGB`` for regulated values that are
``round()`` and ``clamp()`` to ``range(0, 256)``.

.. code:: python

   c = ColorRGB(255, 174.5, 0) # nearly orange
   assert c.rgb == (255, 174.5, 0) # lowercase = real values
   assert c.RGB == (255, 174, 0)   # uppercase = regulated values


.. _ColorHSV:

class ``ColorHSV(H, S, V)``
-----------------------------------------------------------------------------
class ``ColorHSV('@HHH,SSS,VVV')``
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


class ``ColorCompound(fg=None, bg=None)``
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


``decolor(s)``
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

Note that all these colors are mapped to the nearest xterm 256 color, which
makes their values duplicate *a lot*.
Their RGB value are likely *not* consistent with W3C's definition.

.. _w3c_color_list: https://www.w3.org/TR/css-color-3/#svg-color
__ w3c_color_list_

* ``aliceblue`` (15)
* ``antiquewhite`` (230)
* ``aqua`` (14)
* ``aquamarine`` (122)
* ``azure`` (15)
* ``beige`` (230)
* ``bisque`` (224)
* ``black`` (0 black)
* ``blanchedalmond`` (230)
* ``blue`` (12)
* ``blueviolet`` (92)
* ``brown`` (124)
* ``burlywood`` (180)
* ``cadetblue`` (73)
* ``chartreuse`` (118)
* ``chocolate`` (166)
* ``clementine`` (166)
* ``coral`` (209)
* ``cornflowerblue`` (69)
* ``cornsilk`` (230)
* ``crimson`` (161)
* ``cyan`` (14)
* ``darkblue`` (18)
* ``darkcyan`` (30)
* ``darkgoldenrod`` (136)
* ``darkgray`` / ``darkgrey`` (248)
* ``darkgreen`` (22)
* ``darkkhaki`` (143)
* ``darkmagenta`` (90)
* ``darkolivegreen`` (239)
* ``darkorange`` (208)
* ``darkorchid`` (98)
* ``darkred`` (88)
* ``darksalmon`` (174)
* ``darkseagreen`` (108)
* ``darkslateblue`` (60)
* ``darkslategray`` / ``darkslategrey`` (238)
* ``darkturquoise`` (44)
* ``darkviolet`` (92)
* ``deeppink`` (198)
* ``deepskyblue`` (39)
* ``dimgray`` / ``dimgrey`` (242)
* ``dodgerblue`` (33)
* ``firebrick`` (124)
* ``floralwhite`` (15)
* ``forestgreen`` (28)
* ``fuchsia`` (13)
* ``gainsboro`` (253)
* ``ghostwhite`` (15)
* ``gold`` (220)
* ``goldenrod`` (178)
* ``gray`` / ``grey`` (8 gray)
* ``green`` (2 green)
* ``greenyellow`` (154)
* ``honeydew`` (255)
* ``hotpink`` (205)
* ``indianred`` (167)
* ``indigo`` (54)
* ``ivory`` (15)
* ``khaki`` (222)
* ``lavender`` (255)
* ``lavenderblush`` (15)
* ``lawngreen`` (118)
* ``lemonchiffon`` (230)
* ``lightblue`` (152)
* ``lightcoral`` (210)
* ``lightcyan`` (195)
* ``lightgoldenrodyellow`` (230)
* ``lightgray`` / ``lightgrey`` (252)
* ``lightgreen`` (120)
* ``lightpink`` (217)
* ``lightsalmon`` (216)
* ``lightseagreen`` (37)
* ``lightskyblue`` (117)
* ``lightslategray`` / ``lightslategrey`` (102)
* ``lightsteelblue`` (152)
* ``lightyellow`` (230)
* ``lime`` (10)
* ``limegreen`` (77)
* ``linen`` (255)
* ``magenta`` (13)
* ``maroon`` (1 maroon)
* ``mediumaquamarine`` (79)
* ``mediumblue`` (20)
* ``mediumorchid`` (134)
* ``mediumpurple`` (98)
* ``mediumseagreen`` (71)
* ``mediumslateblue`` (99)
* ``mediumspringgreen`` (48)
* ``mediumturquoise`` (80)
* ``mediumvioletred`` (162)
* ``midnightblue`` (17)
* ``mintcream`` (15)
* ``mistyrose`` (224)
* ``moccasin`` (223)
* ``murasaki`` (135)
* ``navajowhite`` (223)
* ``navy`` (4 navy)
* ``oldlace`` (230)
* ``olive`` (3 olive)
* ``olivedrab`` (64)
* ``orange`` (214)
* ``orangered`` (202)
* ``orchid`` (170)
* ``palegoldenrod`` (223)
* ``palegreen`` (120)
* ``paleturquoise`` (159)
* ``palevioletred`` (168)
* ``papayawhip`` (230)
* ``peachpuff`` (223)
* ``peru`` (173)
* ``pink`` (218)
* ``plum`` (182)
* ``powderblue`` (152)
* ``purple`` (5 purple)
* ``red`` (9 red)
* ``rosybrown`` (138)
* ``royalblue`` (62)
* ``saddlebrown`` (94)
* ``salmon`` (209)
* ``sandybrown`` (215)
* ``seagreen`` (29)
* ``seashell`` (255)
* ``sienna`` (130)
* ``silver`` (7 silver)
* ``skyblue`` (117)
* ``slateblue`` (62)
* ``slategray`` / ``slategrey`` (66)
* ``snow`` (15)
* ``springgreen`` (48)
* ``steelblue`` (67)
* ``tan`` (180)
* ``teal`` (6 teal)
* ``thistle`` (182)
* ``tomato`` (203)
* ``turquoise`` (80)
* ``violet`` (213)
* ``wheat`` (223)
* ``white`` (15)
* ``whitesmoke`` (255)
* ``yellow`` (11)
* ``yellowgreen`` (113)


``nocolor``
-----------------------------------------------------------------------------
A special color name that has the following properties:

.. code:: python

   assert nocolor == color()
   assert str(nocolor) == '\033[m'
   assert '{}'.format(nocolor) == '\033[m'
   assert nocolor('anything') == 'anything'


``gradient(A, B, N=None, reverse=False, clockwise=None)``
-----------------------------------------------------------------------------
Produces a series of colors from ``A`` to ``B`` of length ``N >= 2``.

.. code:: python

   g = gradient(A, B, N) # [A, ..., B]

If ``A`` and ``B`` are different Color types, ``(A, B)`` is returned.

For Color256 colors, a discrete gradient path is calculated on xterm 256 color cube.
RGB range (``range(16, 232)``) and Grayscale range (``range(232,256)``)
are defined as not compatible to each other.

Keyword argument ``reverse=True`` could be specified to reverse the result.

For ColorHSV colors, keyword argument ``clockwise=True`` / ``clockwise=False``
could be specified to force the gradient sequence to be clockwise or counter-clockwise.
If not specified, a shorter gradient sequence is preferred.
