import smol

import random


def main():
    # a, b = 77, 147
    a, b = 70, 191
    # a, b = random.sample(range(16, 232), 2)
    A = smol.color(a)
    B = smol.color(b)
    for color in smol.gradient(A, B):
        print(smol.paint(color)(color))


if __name__ == '__main__':
    main()
