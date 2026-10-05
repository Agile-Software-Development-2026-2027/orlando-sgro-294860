import re
import sys
from pathlib import Path

from check import normalize, read, require

USAGE = "usage: python3 lint.py <your output>"
NAME = "[a-z0-9_]+"
NUMBER = "0|[1-9][0-9]*"
PAIR = NAME + ":[1-9][0-9]*"
ERRORS = "invalid command|unknown station|already in|not in|no track|already closed|not closed"
SHAPES = [
    "OK|YES|NO|none|UNREACHABLE",
    NUMBER,
    "ERROR (" + ERRORS + ")",
    NAME + "( " + NAME + ")*",
    PAIR + "( " + PAIR + ")*",
]
LINE = re.compile("|".join(SHAPES))


def first_error(output):
    for number, line in enumerate(normalize(output), start=1):
        answer = "answer " + str(number) + ": "
        if any(ord(char) > 127 for char in line):
            return answer + "non-ASCII character"
        if not LINE.fullmatch(line):
            return answer + "unexpected format " + repr(line)
    return None


def main():
    if len(sys.argv) != 2:
        sys.exit(USAGE)
    output = Path(sys.argv[1])
    require([output], USAGE)
    error = first_error(read(output))
    print("Y" if error is None else "N " + error)
    sys.exit(0 if error is None else 1)


if __name__ == "__main__":
    main()
