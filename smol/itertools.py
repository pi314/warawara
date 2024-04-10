def lookahead(iterable):
    it = iter(iterable)
    lookahead = next(it)

    for val in it:
        yield lookahead, False
        lookahead = val

    yield lookahead, True



def selftest():
    from . import selftest
    section = selftest.section
    EXPECT_EQ = selftest.EXPECT_EQ

    section('nocolor test')

    data = []
    for val, is_last in lookahead([1, 2, 3, 4, 5]):
        data.append((val, is_last))

    EXPECT_EQ(data, [
        (1, False),
        (2, False),
        (3, False),
        (4, False),
        (5, True),
        ])
