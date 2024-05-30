def lookahead(iterable):
    it = iter(iterable)
    lookahead = next(it)

    for val in it:
        yield lookahead, False
        lookahead = val

    yield lookahead, True


def flatten(listlist):
    from itertools import chain
    wrapper_type = type(listlist)
    return wrapper_type(chain.from_iterable(listlist))
