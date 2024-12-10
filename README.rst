===============================================================================
Warawara
===============================================================================
A swiss-knife-like library that collects cute utilities for my other projects.

This library only depends on Python standard library and Python itselfs.
It's functionalities will not depend on any third-party packages in a foreseeable future.

Examples:

..  code::python3

    # color strings
    import warawara
    warawara.orange('TEXT')   # \e[38;5;208mTEXT\e[m

    # Invoke external commands and receive the result
    p = warawara.run(['seq', '5'])
    p.stdout.lines  # ['1', '2', '3', '4', '5']

    # Invoke external commands and receive the result, in parallel
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


Test
***************************************************************************

Testing:

..  code:: shell

    $ runtest.sh

With coverage_:

..  code:: shell

    $ pipx install coverage[toml]
    $ coverage run
    $ coverage html

.. _coverage: https://coverage.readthedocs.io/en/latest/index.html
