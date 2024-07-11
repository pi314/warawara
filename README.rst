===============================================================================
Smol
===============================================================================
A small library that provides might-be-useful code for my other projects


..  code::python3

    import smol
    smol.orange('TEXT')   # \e[38;5;208mTEXT\e[m

    p = smol.run(['seq', '5'])
    p.stdout.lines  # ['1', '2', '3', '4', '5']


    p1 = smol.command(['seq', '5'])

    def func(streams, *args):
        for line in streams[0]:
            streams[1].writeline('smol: {}'.format(line))
    p2 = smol.command(func, stdin=True)

    smol.pipe(p1.stdout, p2.stdin)
    p1.run()
    p2.run()
    p2.stdout.lines   # ['smol: 1', 'smol: 2', 'smol: 3', 'smol: 4', 'smol: 5']


Test
***************************************************************************

Testing

..  code:: shell

    $ python3 runtest.py

If coverage_ package is installed, it will be called to generate report into ``htmlcov/``.

.. _coverage: https://coverage.readthedocs.io/en/7.5.4/index.html
