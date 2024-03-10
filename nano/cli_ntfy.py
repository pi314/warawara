import argparse
import shlex
import sys


from . import lib_cmd
from . import lib_paint


def print_cmd(cmd):

    def color_token(arg):
        token = shlex.quote(arg)
        color = lib_paint.nocolor
        if token.startswith(('"', "'")):
            color = lib_paint.orange
        elif token.startswith('-'):
            color = lib_paint.cyan

        return color(token)

    print(lib_paint.magenta('$'), ' '.join(
        color_token(arg) for arg in cmd
        ))


def notify(title, lines):
    def quote(text):
        return '"' + text.replace('"', r'\"') + '"'

    args = ['display', 'notification', quote(r'\n'.join(lines))]

    if title is not None:
        args += ['with', 'title', quote(title)]

    cmd = ['osascript', '-e', ' '.join(args)]
    print_cmd(cmd)
    exit(lib_cmd.run(cmd).returncode)


def main(argv):
    parser = argparse.ArgumentParser(description='ntfy', prog='ntfy')
    parser.add_argument('-t', '--title', help='Notification title')
    parser.add_argument('lines', nargs='*', help='Notification text', default=[])

    args = parser.parse_args(argv)

    notify(args.title, args.lines)


def cli_main():
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print_err('KeyboardInterrupt')
