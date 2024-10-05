===============================================================================
Warawara
===============================================================================
A small library that provides cute utilities for my other projects


..  code::python3

    import warawara
    warawara.orange('TEXT')   # \e[38;5;208mTEXT\e[m

    p = warawara.run(['seq', '5'])
    p.stdout.lines  # ['1', '2', '3', '4', '5']


    p1 = warawara.command(['seq', '5'])

    def func(streams, *args):
        for line in streams[0]:
            streams[1].writeline('wara: {}'.format(line))
    p2 = warawara.command(func, stdin=True)

    warawara.pipe(p1.stdout, p2.stdin)
    p1.run()
    p2.run()
    p2.stdout.lines   # ['wara: 1', 'wara: 2', 'wara: 3', 'wara: 4', 'wara: 5']


Test
***************************************************************************

Testing

..  code:: shell

    $ python3 runtest.py

If coverage_ package is installed, it will be called to generate report into ``htmlcov/``.

.. _coverage: https://coverage.readthedocs.io/en/7.5.4/index.html
