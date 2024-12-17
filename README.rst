===============================================================================
Warawara
===============================================================================
A swiss-knife-like library that collects cute utilities for my other projects.

This library only depends on Python standard library and Python itself.
It's functionalities will not depend on any third-party packages in a foreseeable future.

Examples:

..  code::python3

    # color strings
    import warawara
    warawara.orange('TEXT')   # \e[38;5;208mTEXT\e[m

    # Invoke external commands and receive the result
    p = warawara.run(['seq', '5'])
    p.stdout.lines  # ['1', '2', '3', '4', '5']

    # Invoke external commands and receive the result in a non-blocking manner
    p1 = warawara.command(['seq', '5'])

    def func(streams, *args):
        for line in streams[0]:
            streams[1].writeline('wara: {}'.format(line))

    p2 = warawara.command(func, stdin=True)

    warawara.pipe(p1.stdout, p2.stdin)
    p1.run()
    p2.run()
    p2.stdout.lines   # ['wara: 1', 'wara: 2', 'wara: 3', 'wara: 4', 'wara: 5']


From my own perspective, Python's subprocess interface is not friendly enough
for simple uses.


Installation
-----------------------------------------------------------------------------

..  code::shell

    $ pip3 install warawara


Or just copy the whole folder to your machine, and add the path to ``sys.path``:

..  code::python3

    import sys
    sys.path.insert(0, '/Users/cychih/bin/.repo/warawara')
    import warawara


Test
-----------------------------------------------------------------------------

Testing:

..  code:: shell

    $ python3 -m unittest

With `pytest-cov <https://pytest-cov.readthedocs.io/en/latest/>`_:

..  code:: shell

    $ pipx install pytest-cov --include-deps
    $ pytest --cov=warawara --cov-report=html
