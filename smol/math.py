__all__ = ['is_int', 'sgn', 'lerp', 'interval']
__all__ += ['vector']


def is_int(o):
    return isinstance(o, int)


def sgn(i):
    return (i > 0) - (i < 0)


def lerp(a, b, t):
    if t == 0:
        return a
    if t == 1:
        return b
    return a + t * (b - a)


class vector(tuple):
    def __new__(cls, *args, **kwargs):
        if len(args) > 1:
            return super().__new__(cls, args)
        else:
            return super().__new__(cls, *args)

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return vector(i + other for i in self)
        if len(self) != len(other):
            raise ValueError('Cannot operate on vector(len={}) and {}'.format(len(self), other))
        return vector(map(lambda x: x[0] + x[1], zip(self, other)))

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return vector(i - other for i in self)
        if len(self) != len(other):
            raise ValueError('Cannot operate on vector(len={}) and {}'.format(len(self), other))
        return vector(map(lambda x: x[0] - x[1], zip(self, other)))

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return vector(i * other for i in self)
        if len(self) != len(other):
            raise ValueError('Cannot operate on vector(len={}) and {}'.format(len(self), other))
        return vector(map(lambda x: x[0] * x[1], zip(self, other)))

    def __rmul__(self, other):
        return self * other

    def map(self, func):
        return vector(func(i) for i in self)


def interval(a, b, close=True):
    direction = sgn(b - a)
    if direction == 0:
        return [a] if close else []

    ret = range(a, b + direction, direction)
    if close:
        return ret
    return ret[1:-1]


# class matrix:
#     def __init__(self, *args):
#         if len(args) == 2 and is_int(args[0]) and is_int(args[1]):
#             self.rows = args[0]
#             self.cols = args[1]
#             self.data = []
#             for i in range(self.rows):
#                 self.data.append(vector([0] * self.cols))
#
#         elif len(args) == 1 and isinstance(args, (tuple, list)):
#             self.rows = len(args[0])
#             self.cols = len(args[0][0])
#             self.data = []
#             for i, row in enumerate(args[0]):
#                 self.data.append(list(row))
#                 if len(self.data[-1]) != self.cols:
#                     raise ValueError('Incorrect row length:', row)
#
#     def __repr__(self):
#         return 'matrix(rows={}, cols={})'.format(self.rows, self.cols)
#
#     def __mul__(self, other):
#         if self.cols != other.rows:
#             raise ValueError('{}x{} matrix cannot multiply with {}x{} matrix'.format(
#                 self.rows, self.cols, other.rows, other.cols))
#
#         ret = matrix(self.rows, other.cols)
#
#         for row in range(ret.rows):
#             for col in range(ret.cols):
#                 ret.data[row][col] = sum(itertools.starmap(
#                         lambda a, b: a * b,
#                         zip(
#                             self.data[row],
#                             (other.data[col][i] for i in range(ret.cols))
#                             )
#                         ))
#
#         return ret
#
#     def __getitem__(self, key):
#         return self.data[key]
