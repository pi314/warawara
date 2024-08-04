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
            self.rows = args[0]
            self.cols = args[1]
            self.data = []
            for i in range(self.rows):
                self.data.append(vector([0] * self.cols))

        elif len(args) == 1 and isinstance(args, (tuple, list)):
            self.rows = len(args[0])
            self.cols = len(args[0][0])
            self.data = []
            for i, row in enumerate(args[0]):
                self.data.append(list(row))
                if len(self.data[-1]) != self.cols:
                    raise ValueError('Incorrect row length:', row)

    def __repr__(self):
        return 'matrix(rows={}, cols={})'.format(self.rows, self.cols)

    def __mul__(self, other):
        if self.cols != other.rows:
            raise ValueError('{}x{} matrix cannot multiply with {}x{} matrix'.format(
                self.rows, self.cols, other.rows, other.cols))

        ret = matrix(self.rows, other.cols)

        for row in range(ret.rows):
            for col in range(ret.cols):
                ret.data[row][col] = sum(map(
                        lambda a: a[0] * a[1],
                        zip(
                            self.data[row],
                            (other.data[col][i] for i in range(ret.cols))
                            )
                        ))

        return ret

    def __getitem__(self, key):
        return self.data[key]
