import smol

import random


def main():
    # a, b = 77, 147
    a, b = 70, 191
    # a, b = random.sample(range(16, 232), 2)
    # print(smol.color, super(smol.color))
    # print(smol.color256, super(smol.color256))
    # print(smol.rgb, super(smol.rgb))
    # assert False
    # A = smol.color(a)
    # B = smol.color(b)
    # print(smol.paint(smol.rgb('#FF5F00'))('test'))
    # for color in smol.gradient(A, B):
    #     print(smol.paint(color)(color))

    A = smol.color(241)
    B = smol.color(250)
    for color in smol.gradient(A, B, N=4):
        print(smol.paint(color)(color))


if __name__ == '__main__':
    main()
