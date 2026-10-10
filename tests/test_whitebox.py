# pylint: disable=missing-function-docstring missing-module-docstring missing-class-docstring
import pytest

from solution import (
    GatesManager,
    calculate_fare,
    calculate_total_fare,
    connessioni,
    stazioni,
)

# Before going forward: these tests are, I hope it's clear, pretty sparse
# I did multiple files because I wanted to show different types of tests
#   I normally do 1 file 1 test_file to keep stuff organized
# Doing things this way made my brain smoke, so I went with the easy route and spammed classes
# I could have done it with 1 test class but whatever it's "more granular" this way
# and yeah the """ comment """ in python is atrocious, I will not use it
# Note: It might be good to split the tests into multiple function to be more even more granular,
#   but I don't like walls of function of 1/2 lines of code

# -------- DATA PREPPING --------


@pytest.fixture
def small_manager():
    stations = ["A", "B", "C", "D"]
    connections = {
        "A": ["B"],
        "B": ["A", "C"],
        "C": ["B"],
        "D": [],
    }
    return GatesManager(connections=connections, stations=stations)


@pytest.fixture
def default_manager():
    return GatesManager(connessioni, stazioni)


# -------- EXTENRAL FUNCTIONS --------


@pytest.mark.parametrize(
    "trips, expected",
    [
        (1, 2),
        (3, 2),
        (4, 1),
        (5, 1),
        (6, 0),
        (10, 0),
    ],
)
def test_calculate_fare_tiers(trips, expected):
    assert calculate_fare(trips) == expected


@pytest.mark.parametrize(
    "trips, expected_total",
    [
        (0, 0),
        (1, 2),  # 2
        (3, 6),  # 2 + 2 + 2
        (4, 7),  # 6 + 1
        (5, 8),  # 6 + 1 + 1
        (6, 8),  # 8 + 0
    ],
)
def test_calculate_total_fare_accumulation(trips, expected_total):
    assert calculate_total_fare(trips) == expected_total


# -------- INTERNAL FUNCTIONS --------


class TestGatesManagerWhiteboxInternals:
    def test_can_go_shortest_path_dijkstra_found(self, small_manager):
        assert small_manager.__can_go_shortest_path_bfs__("A", "C") == ["A", "B", "C"]
        assert small_manager.__can_go_shortest_path_bfs__("C", "A") == ["C", "B", "A"]

    def test_can_go_shortest_path_dijkstra_unreachable(self, small_manager):
        assert small_manager.__can_go_shortest_path_bfs__("A", "D") == []

    def test_can_go_shortest_path_dijkstra_unknown_station(self, small_manager):
        assert small_manager.__can_go_shortest_path_bfs__("A", "NON_EXISTENT") == []

    def test_can_go_boolean(self, small_manager):
        assert small_manager.__can_go__("A", "C") is True
        assert small_manager.__can_go__("A", "D") is False

    def test_can_go_shortest_path_bfs_same_station(self, small_manager):
        assert small_manager.__can_go_shortest_path_bfs__("A", "A") == ["A"]


class TestGatesManagerUserState:
    def test_enter_updates_internal_state(self, small_manager):
        res = small_manager.enter("alice", "A")
        assert res == "OK"
        assert small_manager.inside["alice"] is True
        assert small_manager.station_history["A"]["alice"] == 1

    def test_enter_errors(self, small_manager):
        assert small_manager.enter("alice", "UNKNOWN") == "ERROR unknown station"
        small_manager.enter("alice", "A")
        assert small_manager.enter("alice", "B") == "ERROR already in"

    def test_exit_updates_history_and_cost(self, small_manager):
        small_manager.enter("bob", "A")
        fare = small_manager.exit("bob", "B")

        assert fare == "2"
        assert small_manager.inside["bob"] is False
        assert small_manager.history["bob"] == 1
        assert small_manager.station_history["B"]["bob"] == 1

    def test_exit_errors(self, small_manager):
        assert small_manager.exit("charlie", "UNKNOWN") == "ERROR unknown station"
        assert small_manager.exit("charlie", "A") == "ERROR not in"

    def test_pending_sorting(self, small_manager):
        small_manager.history = {"alice": 5, "bob": 2, "charlie": 2}
        small_manager.inside = {"alice": True, "bob": True, "charlie": True}

        assert small_manager.pending() == "bob charlie alice"

    def test_pending_empty(self, small_manager):
        assert small_manager.pending() == "none"

    def test_regulars_sorting(self, small_manager):
        small_manager.station_history["A"] = {
            "alice": 3,
            "bob": 5,
            "charlie": 5,
        }

        assert small_manager.regulars("A") == "bob:5 charlie:5 alice:3"

    def test_regulars_empty_and_unknown(self, small_manager):
        assert small_manager.regulars("NON_ESISTE") == "ERROR unknown station"
        assert small_manager.regulars("A") == "none"

    def test_enter_and_exit_station_missing_from_station_history(self, small_manager):
        small_manager.stations.append("EXTRA")

        assert small_manager.enter("alice", "EXTRA") == "OK"
        assert small_manager.station_history["EXTRA"]["alice"] == 1

        del small_manager.station_history["EXTRA"]
        assert small_manager.exit("alice", "EXTRA") == "2"
        assert small_manager.station_history["EXTRA"]["alice"] == 1


class TestGatesManagerTracksAndRoutes:
    def test_closed_and_open_toggle(self, small_manager):
        assert small_manager.closed("A", "B") == "OK"
        assert small_manager.graph.get_bidirectional_edge_status("A", "B") is False

        assert small_manager.closed("A", "B") == "ERROR already closed"

        assert small_manager.open("A", "B") == "OK"
        assert small_manager.graph.get_bidirectional_edge_status("A", "B") is True
        assert small_manager.open("A", "B") == "ERROR not closed"

    def test_closed_errors(self, small_manager):
        assert small_manager.closed("A", "Z") == "ERROR unknown station"
        assert small_manager.closed("A", "C") == "ERROR no track"

    def test_open_errors(self, small_manager):
        assert small_manager.open("A", "Z") == "ERROR unknown station"
        assert small_manager.open("Z", "A") == "ERROR unknown station"
        assert small_manager.open("A", "C") == "ERROR no track"

    def test_reachable_and_route_with_closed_connection(self, small_manager):
        assert small_manager.reachable("A", "C") == "YES"
        assert small_manager.route("A", "C") == "A B C"

        small_manager.closed("A", "B")

        assert small_manager.reachable("A", "C") == "NO"
        assert small_manager.route("A", "C") == "UNREACHABLE"

    def test_reachable_same_station(self, small_manager):
        assert small_manager.reachable("A", "A") == "YES"
        assert small_manager.route("A", "A") == "A"

    def test_reachable_and_route_unknown_station(self, small_manager):
        assert small_manager.reachable("A", "Z") == "ERROR unknown station"
        assert small_manager.reachable("Z", "A") == "ERROR unknown station"
        assert small_manager.route("A", "Z") == "ERROR unknown station"
        assert small_manager.route("Z", "A") == "ERROR unknown station"
