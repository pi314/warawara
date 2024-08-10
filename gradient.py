import smol

import random


def main():
    import sys
    argv = sys.argv[1:]

    try:
        a = int(argv[0])
        b = int(argv[1])
        argv.pop(0)
        argv.pop(0)

        if argv:
            n = int(argv[0])
        else:
            n = None

    except IndexError:
        a, b = random.sample(range(16, 232), 2)
        n = None

    # a, b = 77, 147
    # a, b = 70, 191
    # a, b = 70, 227
    # a, b = 232, 255
    # a, b = 214, 39
    # a, b = random.sample(range(16, 232), 2)
    # a, b = b, a
    # print(smol.dye, super(smol.dye))
    # print(smol.dye256, super(smol.dye256))
    # print(smol.rgb, super(smol.rgb))
    A = smol.dye(a)
    B = smol.dye(b)
    A = smol.dye('#FF0000')
    B = smol.dye('#00FF00')
    # A = smol.dye('#FFAF00')
    # B = smol.dye('#00AFFF')
    n = 10
    # A = smol.dye('#FF1100')
    # B = smol.dye('#FF0011')
    # A = smol.dye('#6E3A08')
    # B = smol.dye('#003847')
    for dye in smol.gradient(A, B, N=n):
        print(str(dye) + repr(dye) + '\033[m')

    # A = smol.dye(241)
    # B = smol.dye(250)
    # for dye in smol.gradient(A, B, N=4):
    #     print(smol.paint(dye)(dye))

    # print(smol.paint(smol.rgb('#FF5F00'))('test'))


if __name__ == '__main__':
    main()
