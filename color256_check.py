import sys
import re

import warawara as wara


def main():
    data = []

    def FG(R, G, B):
        if R > 0xC0 or G > 0xC0 or B > 0xFF:
            return wara.black
        return wara.white

    def RGB(R, G, B):
        int24 = (R << 16) | (G << 8) | B
        return '#' + hex(int24)[2:].rjust(6, '0')

    for i in range(256):
        if i < 16:
            base = 0xFF if (i > 7) else 0x80
            R = base * ((i & 0x1) != 0) + (0x40 * (i == 7)) + (0x80 * (i == 8))
            G = base * ((i & 0x2) != 0) + (0x40 * (i == 7)) + (0x80 * (i == 8))
            B = base * ((i & 0x4) != 0) + (0x40 * (i == 7)) + (0x80 * (i == 8))

        elif i in range(16, 232):
            index_R = ((i - 16) // 36)
            index_G = (((i - 16) % 36) // 6)
            index_B = ((i - 16) % 6)
            R = (55 + index_R * 40) if index_R > 0 else 0
            G = (55 + index_G * 40) if index_G > 0 else 0
            B = (55 + index_B * 40) if index_B > 0 else 0

        else:
            R = G = B = (i - 232) * 10 + 8

        data.append((R, G, B, RGB(R, G, B), []))

    with open('color_css.txt') as f:
        for line in f:
            line = line.strip()
            m = re.match(r'^(\w+) +(#[0-9A-F]{6}) +(\d+),(\d+),(\d+)$', line)
            if not m:
                print(line)
                sys.exit(1)

            name, rgbhex, R, G, B = m.groups()
            R = int(R, 10)
            G = int(G, 10)
            B = int(B, 10)

            if False:
                pass

            elif name in ('antiquewhite', 'blanchedalmond'):
                near = 230

            elif name == 'midnightblue':
                near = 17

            elif name == 'skyblue':
                near = 117

            else:
                near = None
                near_dist = 0x7fffffff
                for i in range(256):
                    dist = ((data[i][0] - R)**2 + (data[i][1] - G)**2 + (data[i][2] - B)**2)
                    if dist < near_dist:
                        near_dist = dist
                        near = i

            if near is not None:
                data[near][4].append((RGB(R, G, B), name))


    for i in range(256):
        a = wara.paint(fg=FG(*data[i][:3]), bg=i)(' ' + str(i).ljust(5) + '  ')
        b = (FG(*data[i][:3]) / wara.ColorRGB(data[i][:3]))('  ' + data[i][3] + '  ')

        if data[i][4]:
            c = ''.join(
                    [(FG(*data[i][:3]) / wara.ColorRGB(t[0]))('  ' + ((t[1]))) for t in data[i][4]] +
                    [(FG(*data[i][:3]) / wara.ColorRGB(data[i][:3]))(' ' * (120 - sum([len(t[1]) + 2 for t in data[i][4]])))]
                    )
        else:
            c = (FG(*data[i][:3]) / wara.ColorRGB(data[i][:3]))(' ' * 120)

        print(a + b + c)


if __name__ == '__main__':
    print()
    main()
