__all__ = ['lerp']
__all__ += ['vector']


def is_int(o):
    return isinstance(o, int)


def lerp(a, b, t):
    if t == 0:
        return a
    if t == 1:
        return b
    return a + t * (b - a)


class vector(list):
    def __init__(self, *args):
        super().__init__(*args)

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return vector(i + other for i in self)
        return vector(map(lambda x: x[0] + x[1], zip(self, other)))

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return vector(i - other for i in self)
        return vector(map(lambda x: x[0] - x[1], zip(self, other)))

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return vector(i * other for i in self)
        raise TypeError("Not supported operation")

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return vector(i * other for i in self)
        raise TypeError("Not supported operation")

    def map(self, func):
        return vector(func(i) for i in self)


class matrix:
    def __init__(self, *args):
        if len(args) == 2 and is_int(args[0]) and is_int(args[1]):
            self.M = args[0]
            self.N = args[1]
            self.data = []
            for i in range(self.M):
                self.data.append(vector([0] * self.N))
