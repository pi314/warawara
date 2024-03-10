import argparse
import datetime
import sys
import threading
import time

from . import lib_cmd


def print_err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def listener(cmd, delay, stop_signal):
    line_count = 0

    # Get initial content from command for excluding it
    p = lib_cmd.run(cmd)
    if p.returncode:
        return

    old_lines = p.stdout

    while True:
        if stop_signal.is_set():
            break

        p = lib_cmd.run(cmd)

        if p.returncode:
            break

        new_lines = p.stdout

        if old_lines != new_lines:
            for line in new_lines:
                print(line)

                # Print timestamp for reference so you know what's going on
                if not sys.stdout.isatty():
                    print_err('[' + str(datetime.datetime.now()) + ']', line)

                line_count += 1

            old_lines = new_lines

            lib_cmd.run(['ntfy', '-t', 'Copied', '{} lines'.format(line_count)])

        if cmd[0] != 'sleep':
            time.sleep(delay)


def main(argv):
    parser = argparse.ArgumentParser(prog='sponge',
            description='sponge',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--delay', default=0.2, type=float, help='Delay in seconds')
    parser.add_argument('command', nargs='*', default=None, help='Command to run')

    args = parser.parse_args(argv)

    if not args.command:
        lines = [line.rstrip() for line in sys.stdin.readlines()]

        for line in lines:
            print(line)

        exit()

    stop_signal = threading.Event()

    cmd_thread = threading.Thread(target=listener, args=(args.command, args.delay, stop_signal))
    cmd_thread.daemon = True
    cmd_thread.start()

    for line in sys.stdin:
        print(line.rstrip())

    stop_signal.set()

    cmd_thread.join()


def cli_main():
    main(sys.argv[1:])


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print_err('KeyboardInterrupt')
