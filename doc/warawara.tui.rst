===============================================================================
``warawara.tui``
===============================================================================

This document describes the API set provided by ``warawara.tui``.

For the index of this package, see `warawara.rst <warawara.rst>`_.

.. contents:: Table of Contents


``strwidth(s)``
-----------------------------------------------------------------------------
Return the display "width" of the string.

Printable ASCII characters are count as width 1, and CJK characters are count as width 2.

Color escape sequences are ignored.

.. code:: python

   assert strwidth('test') == 4
   assert strwidth('\033[38;5;214mtest\033[m') == 4
   assert strwidth('哇嗚') == 4


``ljust(data, width=None, fillchar=' ')``
-----------------------------------------------------------------------------
``rjust(data, width=None, fillchar=' ')``
-----------------------------------------------------------------------------
``ljust`` / ``rjust`` ``data`` based on ``strwidth()``.

If ``data`` is a ``str``, the behavior is similar to ``str.ljust`` and ``str.rjust``.

.. code:: python

   assert ljust('test', 10) == 'test      '
   assert rjust('test', 10) == '      test'

If ``data`` is a 2-dimensional list of ``str``, each columns are aligned separately.

.. code:: python

   data = [
       ('column1', 'col2'),
       ('word1', 'word2'),
       ('word3', 'word4 long words'),
       ]

   assert ljust(data) == [
       ('column1', 'col2            '),
       ('word1  ', 'word2           '),
       ('word3  ', 'word4 long words'),
       ]


class ``ThreadedSpinner``
-----------------------------------------------------------------------------
Displays a pipx-inspired spinner on screen.

The spinner runs in a separated daemon thread.

Three sequences of icons are defined for different displaying stages:

* Entry
* Loop
* Leave

The "entry" sequence is displayed once, and the "loop" sequence is repeated.

Before the animation finishes, the "leave" sequence is displayed.


``ThreadedSpinner(*icon, delay=0.1)``
***************************************************************************

Note the ``*icon`` constructs a list of arguments.

* If ``icon`` is not specified:

  - Entry sequence is set to ``⠉ ⠛ ⠿ ⣿ ⠿ ⠛ ⠉ ⠙`` (without the white spaces)
  - Loop sequence is set to ``⠹ ⢸ ⣰ ⣤ ⣆ ⡇ ⠏ ⠛`` (without the white spaces)
  - Leave sequence is set to ``⣿``

* If ``icon`` is a single string, it's used as the loop sequence

  - And leave sequence is set to ``.``

* If ``icon`` contains two strings, they are used as entry and loop sequences, respectively.

  - And leave sequence is set to ``.``

* If ``icon`` contains three strings, they are used as entry, loop, and leave sequences, respectively.
