# pylint: disable=missing-function-docstring missing-module-docstring missing-class-docstring
import io
import runpy

import pytest

import solution

# -------- DATA PREPPING --------


@pytest.fixture
def run_cli(monkeypatch, capsys):
    def _execute(commands: list[str]) -> list[str]:
        raw_input = "\n".join(commands) + "\n"
        monkeypatch.setattr("sys.stdin", io.StringIO(raw_input))
        solution.main()
        captured = capsys.readouterr()
        return [line for line in captured.out.strip().splitlines() if line]

    return _execute


@pytest.fixture
def base_traffic():
    return [
        "TAPIN alice garibaldi",
        "TAPOUT alice universita",
        "TAPIN bob toledo",
        "TAPIN charlie garibaldi",
    ]


# -------- INTERNAL(?) FUNCTIONS --------


def test_single_command_flow(run_cli):
    cmds = [
        "TAPIN u1 dante",
        "PENDING",
        "TAPOUT u1 museo",
        "FARE u1",
    ]
    assert run_cli(cmds) == [
        "OK",
        "u1",
        "2",
        "2",
    ]


def test_blackbox_with_preloaded_state(run_cli, base_traffic):
    test_commands = base_traffic + [
        "PENDING",
        "REGULARS garibaldi",
        "FARE alice",
    ]
    output = run_cli(test_commands)

    assert output[-3:] == [
        "bob charlie",
        "alice:1 charlie:1",
        "2",
    ]


def test_network_closures_and_queries(run_cli):
    cmds = [
        "ROUTE universita municipio",
        "CLOSED universita municipio",
        "REACHABLE universita municipio",
        "OPEN universita municipio",
        "REACHABLE universita municipio",
    ]
    assert run_cli(cmds) == [
        "universita municipio",
        "OK",
        "NO",
        "OK",
        "YES",
    ]


@pytest.mark.parametrize(
    "invalid_command",
    [
        "SALTO_IL_TURNELLO alice",
        "TAPIN",
        "ROUTE toledo",
        "INVALID_COMMAND_NAME 1 2 3",
    ],
)
def test_invalid_syntax_triggers_error(run_cli, invalid_command):
    assert run_cli([invalid_command]) == ["ERROR invalid command"]


def test_blackbox_empty_lines_and_whitespace(run_cli):
    cmds = [
        "",
        "   ",
        "PENDING",
        "",
        "REGULARS garibaldi",
        "   ",
    ]
    output = run_cli(cmds)
    assert output == [
        "none",
        "none",
    ]


def test_blackbox_not_found_errors(run_cli):
    cmds = [
        "REGULARS stazione_fantasma",
        "OPEN stazione_fantasma garibaldi",
        "OPEN garibaldi toledo",
        "REACHABLE garibaldi stazione_fantasma",
        "ROUTE stazione_fantasma garibaldi",
    ]
    output = run_cli(cmds)
    assert output == [
        "ERROR unknown station",
        "ERROR unknown station",
        "ERROR no track",
        "ERROR unknown station",
        "ERROR unknown station",
    ]


def test_main_execution_entrypoint(monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("PENDING\n"))
    runpy.run_module("solution", run_name="__main__")
