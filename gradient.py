import smol

import random


def main():
    # a, b = 77, 147
    a, b = 70, 191
    a, b = 214, 39
    # a, b = random.sample(range(16, 232), 2)
    # print(smol.color, super(smol.color))
    # print(smol.color256, super(smol.color256))
    # print(smol.rgb, super(smol.rgb))
    A = smol.color(a)
    B = smol.color(b)
    # A = smol.color('#FF0000')
    # B = smol.color('#00FF00')
    # A = smol.color('#FFAF00')
    # B = smol.color('#00AFFF')
    # A = smol.color('#FF1100')
    # B = smol.color('#FF0011')
    # A = smol.color('#6E3A08')
    # B = smol.color('#003847')
    for color in smol.gradient(A, B):
        print(smol.paint(color)(color))

    # A = smol.color(241)
    # B = smol.color(250)
    # for color in smol.gradient(A, B, N=4):
    #     print(smol.paint(color)(color))

    # print(smol.paint(smol.rgb('#FF5F00'))('test'))


if __name__ == '__main__':
    main()
