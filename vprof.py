import cProfile
import curses
import io
import pstats


_KEYS = [
    'calls',
    'tottime',
    'cumtime',
    'nfl',
]


def _get_lines(pr, sortby):
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    return s.getvalue().split('\n')


def main_loop(stdscr, pr):
    n_header = 5

    scroll = 0
    line_cursor = 0
    sort_cursor = 0

    while True:
        sortby = _KEYS[sort_cursor]
        lines = _get_lines(pr, sortby)

        header = lines[:n_header]
        lines = lines[n_header:]

        height, width = stdscr.getmaxyx()
        height -= n_header

        stdscr.clear()

        for i, line in enumerate(header):
            stdscr.addstr(i, 0, line)

        for i, line in enumerate(lines[scroll:scroll + height]):
            if i + scroll == line_cursor:
                stdscr.addstr(i + n_header, 0, line, curses.A_REVERSE)
            else:
                stdscr.addstr(i + n_header, 0, line)

        x = stdscr.getch()
        if x == ord('q'):
            break
        elif x == ord('j') and line_cursor + 1 < len(lines):
            line_cursor += 1
        elif x == ord('k') and line_cursor - 1 >= 0:
            line_cursor -= 1
        elif x == ord('>') and sort_cursor + 1 < len(_KEYS):
            sort_cursor += 1
        elif x == ord('<') and sort_cursor - 1 >= 0:
            sort_cursor -= 1

        if line_cursor < scroll:
            scroll = line_cursor
        if line_cursor >= scroll + height:
            scroll = line_cursor - height + 1
        curses.flash()


def view(pr):
    curses.wrapper(main_loop, pr)


def runctx(statement, globals, locals):
    prof = cProfile.Profile()
    result = None
    try:
        prof = prof.runctx(statement, globals, locals)
    except SystemExit:
        pass
    view(prof)


def main():
    import argparse
    import os
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('arg', nargs='+')
    args = parser.parse_args()
    sys.argv[:] = args.arg

    progname = args.arg[0]
    sys.path.insert(0, os.path.dirname(progname))
    with open(progname, 'rb') as f:
        source = f.read()
    code = compile(source, progname, 'exec')
    globs = {
        '__file__': progname,
        '__name__': '__main__',
        '__package__': None,
    }
    runctx(code, globs, None)


if __name__ == '__main__':
    main()
