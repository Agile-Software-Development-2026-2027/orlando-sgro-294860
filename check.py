import sys
from itertools import zip_longest
from pathlib import Path

USAGE = "usage: python3 check.py <input> <your output> <official output>"


def require(paths, usage):
    missing = [path for path in paths if not path.is_file()]
    if missing:
        sys.exit(str(missing[0]) + " not found\n" + usage)


def normalize(text):
    return [" ".join(line.split()) for line in text.splitlines() if line.strip()]


def read(path):
    return path.read_bytes().decode("utf-8", errors="replace")


def commands(text):
    numbered = enumerate(text.splitlines(), start=1)
    return [
        (number, " ".join(line.split())) for number, line in numbered if line.strip()
    ]


def first_mismatch(asked, expected, got):
    rows = zip_longest(asked, expected, got, fillvalue=None)
    for (number, command), want, have in (
        (row[0] or (0, ""), row[1], row[2]) for row in rows
    ):
        if want != have:
            where = (
                "line " + str(number) + " " + repr(command)
                if number
                else "after the last command"
            )
            wanted = repr(want) if want else "nothing"
            shown = repr(have) if have else "no output"
            return where + ": expected " + wanted + ", got " + shown
    return None


def hint(asked, got):
    if len(got) == len(asked):
        return ""
    count = str(len(got)) + " output lines for " + str(len(asked)) + " commands"
    if len(got) < len(asked):
        why = "a command printed nothing, or the program stopped early"
    else:
        why = "a command printed more than one line"
    return "\nhint: " + count + ": " + why + ". The mismatch may start earlier."


def main():
    if len(sys.argv) != 4:
        sys.exit(USAGE)
    asked, mine, official = (Path(arg) for arg in sys.argv[1:])
    require([asked, mine, official], USAGE)
    asked, got = commands(read(asked)), normalize(read(mine))
    problem = first_mismatch(asked, normalize(read(official)), got)
    print("PASS" if problem is None else "FAIL " + problem + hint(asked, got))
    sys.exit(0 if problem is None else 1)


if __name__ == "__main__":
    main()
