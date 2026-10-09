import subprocess
import sys
from pathlib import Path

import pytest

from check import commands, first_mismatch, hint, normalize

TEST_DIR = Path("./test-cases")
SOL_DIR = Path("./solutions")

input_files = sorted(TEST_DIR.glob("*.in"))


@pytest.mark.parametrize("in_file", input_files, ids=lambda p: p.stem)
def test_solution_cases(in_file: Path):
    expected_file = SOL_DIR / f"{in_file.stem}.out"
    assert expected_file.exists(), f"Missing file: {expected_file}"

    proc = subprocess.run(
        [sys.executable, "solution.py"],
        input=in_file.read_bytes(),
        capture_output=True,
        timeout=2,
        check=True,
    )
    assert proc.returncode == 0, (
        f"solution.py terminated with error: {proc.stderr.decode()}"
    )

    asked_cmds = commands(in_file.read_text(encoding="utf-8", errors="replace"))
    got_lines = normalize(proc.stdout.decode("utf-8", errors="replace"))
    expected_lines = normalize(
        expected_file.read_text(encoding="utf-8", errors="replace")
    )

    problem = first_mismatch(asked_cmds, expected_lines, got_lines)
    assert problem is None, f"{problem}{hint(asked_cmds, got_lines)}"
