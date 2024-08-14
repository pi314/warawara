import itertools


def unwrap_one(obj):
    try:
        if len(obj) == 1 and not isinstance(obj[0], str) and iter(obj[0]):
            return obj[0]
    except TypeError:
        pass

    return obj


def lookahead(iterable):
    it = iter(iterable)
    lookahead = next(it)

    for val in it:
        yield lookahead, False
        lookahead = val

    yield lookahead, True


def flatten(listlist):
    wrapper_type = type(listlist)
    return wrapper_type(itertools.chain.from_iterable(listlist))


def zip_longest(*iterables, fillvalues=None):
    if not isinstance(fillvalues, (tuple, list)):
        fillvalues = (fillvalues,) * len(iterables)

    iterators = list(map(iter, iterables))

    while True:
        values = []
        cont = False
        for idx, iterator in enumerate(iterators):
            try:
                value = next(iterator)
                cont = True
            except:
                value = fillvalues[idx]

            values.append(value)

        if not cont:
            break

        yield tuple(values)
