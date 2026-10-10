# pylint: disable=missing-function-docstring missing-module-docstring missing-class-docstring
from collections.abc import Iterable

import pytest

from utils.weighted_directed_graph import WeightedDirectedGraph

# -------- DATA PREPPING --------


@pytest.fixture
def empty_graph() -> WeightedDirectedGraph:
    return WeightedDirectedGraph({})


@pytest.fixture
def linear_graph() -> WeightedDirectedGraph:
    """A <-> B <-> C, D isolated."""
    return WeightedDirectedGraph.from_unweighted(
        {
            "A": ["B"],
            "B": ["A", "C"],
            "C": ["B"],
            "D": [],
        }
    )


@pytest.fixture
def directed_cycle_graph() -> WeightedDirectedGraph:
    """A -> B -> C -> A, plus C -> D."""
    return WeightedDirectedGraph.from_unweighted(
        {
            "A": ["B"],
            "B": ["C"],
            "C": ["A", "D"],
            "D": [],
        }
    )


@pytest.fixture
def full_custom_graph() -> WeightedDirectedGraph:
    return WeightedDirectedGraph.from_full(
        {
            "A": [("B", 5, True), ("C", 10, False)],
            "B": [("A", 2, True), ("C", 3, True)],
            "C": [("A", 7, False)],
            "D": [],
        }
    )


# -------- INITIALIZATION --------
# This is needed becase we have lots of different ways to initialize the graph.


class TestGraphInitialization:
    def test_direct_init_and_empty(self, empty_graph: WeightedDirectedGraph) -> None:
        assert not empty_graph.has_node("A")
        assert "A" not in empty_graph
        assert empty_graph.get_neighbors("A") == []

        raw_adj = {"X": {"Y": (4, True)}, "Y": {}}
        graph = WeightedDirectedGraph(raw_adj)
        assert graph.has_node("X")
        assert graph.has_node("Y")
        assert graph["X", "Y"] == (4, True)

    def test_from_unweighted_various_iterables(self) -> None:
        edges: dict[str, Iterable[str]] = {
            "A": ["B", "C"],
            "B": ("C",),
            "C": {"A"},
            "D": [],
        }
        graph = WeightedDirectedGraph.from_unweighted(edges)

        for node in ("A", "B", "C", "D"):
            assert graph.has_node(node)

        assert graph["A", "B"] == (1, True)
        assert graph["A", "C"] == (1, True)
        assert graph["B", "C"] == (1, True)
        assert graph["C", "A"] == (1, True)
        assert graph["D"] == {}

    def test_from_weighted(self) -> None:
        edges: dict[str, Iterable[tuple[str, int]]] = {
            "A": [("B", 5), ("C", 0), ("D", -3)],
            "B": [("A", 12)],
            "C": [],
            "D": [],
        }
        graph = WeightedDirectedGraph.from_weighted(edges)

        assert graph.get_weight("A", "B") == 5
        assert graph.get_weight("A", "C") == 0
        assert graph.get_weight("A", "D") == -3
        assert graph.get_weight("B", "A") == 12

        assert graph.get_edge_status("A", "B") is True
        assert graph.get_edge_status("A", "C") is True
        assert graph.get_edge_status("A", "D") is True
        assert graph.get_edge_status("B", "A") is True

    def test_from_conditional(self) -> None:
        edges: dict[str, Iterable[tuple[str, bool]]] = {
            "A": [("B", True), ("C", False)],
            "B": [("C", False)],
            "C": [],
        }
        graph = WeightedDirectedGraph.from_conditional(edges)

        assert graph["A", "B"] == (1, True)
        assert graph["A", "C"] == (1, False)
        assert graph["B", "C"] == (1, False)
        assert graph.get_neighbors("A") == ["B"]
        assert graph.get_neighbors("B") == []

    def test_from_full(self, full_custom_graph: WeightedDirectedGraph) -> None:
        assert full_custom_graph["A", "B"] == (5, True)
        assert full_custom_graph["A", "C"] == (10, False)
        assert full_custom_graph["B", "A"] == (2, True)
        assert full_custom_graph["B", "C"] == (3, True)
        assert full_custom_graph["C", "A"] == (7, False)
        assert full_custom_graph["D"] == {}

    def test_constructors_with_empty_dict(self) -> None:
        for graph in (
            WeightedDirectedGraph.from_unweighted({}),
            WeightedDirectedGraph.from_weighted({}),
            WeightedDirectedGraph.from_conditional({}),
            WeightedDirectedGraph.from_full({}),
        ):
            assert not graph.has_node("A")
            assert graph.shortest_path("A", "B") == []


# -------- NODES --------


class TestNodeOperations:
    def test_has_node(self, linear_graph: WeightedDirectedGraph) -> None:
        assert linear_graph.has_node("A") is True
        assert linear_graph.has_node("D") is True
        assert linear_graph.has_node("Z") is False

    def test_add_node_new_and_existing(
        self, linear_graph: WeightedDirectedGraph
    ) -> None:
        linear_graph.add_node("E")
        assert linear_graph.has_node("E") is True
        assert linear_graph["E"] == {}
        assert linear_graph.get_neighbors("E") == []

        linear_graph.add_node("A")
        assert linear_graph.has_edge("A", "B") is True
        assert linear_graph["A", "B"] == (1, True)

    def test_remove_node_cleans_up_incoming_and_outgoing_edges(
        self, linear_graph: WeightedDirectedGraph
    ) -> None:
        linear_graph.remove_node("B")

        assert linear_graph.has_node("B") is False
        assert "B" not in linear_graph
        assert linear_graph.has_edge("A", "B") is False
        assert linear_graph.has_edge("C", "B") is False
        assert linear_graph.has_edge("B", "A") is False
        assert linear_graph.get_neighbors("A") == []
        assert linear_graph.get_neighbors("C") == []
        assert linear_graph.has_node("D") is True

    def test_remove_nonexistent_node_is_noop(
        self, linear_graph: WeightedDirectedGraph
    ) -> None:
        linear_graph.remove_node("NON_EXISTENT")
        assert linear_graph.has_node("A") is True
        assert linear_graph.has_edge("A", "B") is True


# -------- EDGES --------


class TestEdgeOperations:
    def test_has_edge_and_contains(
        self, full_custom_graph: WeightedDirectedGraph
    ) -> None:
        assert full_custom_graph.has_edge("A", "B") is True
        assert ("A", "B") in full_custom_graph

        assert full_custom_graph.has_edge("A", "C") is True
        assert ("A", "C") in full_custom_graph

        assert full_custom_graph.has_edge("A", "D") is False
        assert ("A", "D") not in full_custom_graph

        assert full_custom_graph.has_edge("UNKNOWN", "A") is False
        assert ("UNKNOWN", "A") not in full_custom_graph

    def test_had_bidirectional_edge(
        self, full_custom_graph: WeightedDirectedGraph
    ) -> None:
        assert full_custom_graph.had_bidirectional_edge("A", "B") is True
        assert full_custom_graph.had_bidirectional_edge("A", "C") is True
        assert full_custom_graph.had_bidirectional_edge("B", "C") is False
        assert full_custom_graph.had_bidirectional_edge("C", "B") is False
        assert full_custom_graph.had_bidirectional_edge("A", "D") is False
        assert full_custom_graph.had_bidirectional_edge("A", "Z") is False

    def test_add_edge_valid_and_invalid_nodes(
        self, linear_graph: WeightedDirectedGraph
    ) -> None:
        linear_graph.add_edge("A", "D")
        assert linear_graph.has_edge("A", "D") is True
        assert linear_graph["A", "D"] == (1, True)
        assert linear_graph.has_edge("D", "A") is False

        linear_graph.add_edge("D", "D")
        assert linear_graph.has_edge("D", "D") is True

        linear_graph.add_edge("A", "UNKNOWN")
        linear_graph.add_edge("UNKNOWN", "A")
        linear_graph.add_edge("UNKNOWN_1", "UNKNOWN_2")
        assert linear_graph.has_edge("A", "UNKNOWN") is False
        assert linear_graph.has_node("UNKNOWN") is False

    def test_add_edge_overwrites_existing_edge_to_defaults(
        self, full_custom_graph: WeightedDirectedGraph
    ) -> None:
        assert full_custom_graph["A", "C"] == (10, False)
        full_custom_graph.add_edge("A", "C")
        assert full_custom_graph["A", "C"] == (1, True)

    def test_remove_edge(self, linear_graph: WeightedDirectedGraph) -> None:
        linear_graph.remove_edge("A", "B")
        assert linear_graph.has_edge("A", "B") is False
        assert linear_graph.has_edge("B", "A") is True

        linear_graph.remove_edge("A", "B")
        linear_graph.remove_edge("A", "Z")
        linear_graph.remove_edge("Z", "A")

    def test_get_and_set_edge_status(
        self, full_custom_graph: WeightedDirectedGraph
    ) -> None:
        assert full_custom_graph.get_edge_status("A", "B") is True
        assert full_custom_graph.get_edge_status("A", "C") is False
        assert full_custom_graph.get_edge_status("A", "D") is None
        assert full_custom_graph.get_edge_status("UNKNOWN", "A") is None

        full_custom_graph.set_edge_status("A", "B", False)
        assert full_custom_graph.get_edge_status("A", "B") is False
        assert full_custom_graph.get_weight("A", "B") == 5

        full_custom_graph.set_edge_status("A", "C", True)
        assert full_custom_graph.get_edge_status("A", "C") is True
        assert full_custom_graph.get_weight("A", "C") == 10

        full_custom_graph.set_edge_status("A", "D", True)
        full_custom_graph.set_edge_status("UNKNOWN", "A", True)
        assert full_custom_graph.get_edge_status("A", "D") is None

    @pytest.mark.parametrize(
        "ab_open, ba_open, expected",
        [
            (True, True, True),
            (True, False, False),
            (False, True, False),
            (False, False, False),
        ],
    )
    def test_get_bidirectional_edge_status_combinations(
        self, ab_open: bool, ba_open: bool, expected: bool
    ) -> None:
        graph = WeightedDirectedGraph.from_conditional(
            {
                "A": [("B", ab_open)],
                "B": [("A", ba_open)],
            }
        )
        assert graph.get_bidirectional_edge_status("A", "B") is expected
        assert graph.get_bidirectional_edge_status("B", "A") is expected

    def test_get_bidirectional_edge_status_missing_directions(
        self, full_custom_graph: WeightedDirectedGraph
    ) -> None:
        assert full_custom_graph.get_bidirectional_edge_status("B", "C") is None
        assert full_custom_graph.get_bidirectional_edge_status("C", "B") is None
        assert full_custom_graph.get_bidirectional_edge_status("A", "D") is None
        assert full_custom_graph.get_bidirectional_edge_status("A", "UNKNOWN") is None

    def test_set_bidirectional_edge_status(
        self, full_custom_graph: WeightedDirectedGraph
    ) -> None:
        full_custom_graph.set_bidirectional_edge_status("A", "B", False)
        assert full_custom_graph.get_edge_status("A", "B") is False
        assert full_custom_graph.get_edge_status("B", "A") is False
        assert full_custom_graph.get_bidirectional_edge_status("A", "B") is False
        assert full_custom_graph.get_weight("A", "B") == 5
        assert full_custom_graph.get_weight("B", "A") == 2

        full_custom_graph.set_bidirectional_edge_status("A", "B", True)
        assert full_custom_graph.get_bidirectional_edge_status("A", "B") is True

        full_custom_graph.set_bidirectional_edge_status("B", "C", False)
        assert full_custom_graph.get_edge_status("B", "C") is False
        assert full_custom_graph.has_edge("C", "B") is False

    def test_get_and_set_weight(self, full_custom_graph: WeightedDirectedGraph) -> None:
        assert full_custom_graph.get_weight("A", "B") == 5
        assert full_custom_graph.get_weight("A", "C") == 10
        assert full_custom_graph.get_weight("A", "D") is None
        assert full_custom_graph.get_weight("UNKNOWN", "A") is None

        full_custom_graph.set_weight("A", "B", 99)
        assert full_custom_graph.get_weight("A", "B") == 99
        assert full_custom_graph.get_edge_status("A", "B") is True
        assert full_custom_graph.get_weight("B", "A") == 2

        full_custom_graph.set_weight("A", "C", 42)
        assert full_custom_graph.get_weight("A", "C") == 42
        assert full_custom_graph.get_edge_status("A", "C") is False

        full_custom_graph.set_weight("A", "D", 100)
        full_custom_graph.set_weight("UNKNOWN", "A", 100)
        assert full_custom_graph.get_weight("A", "D") is None

    def test_get_neighbors_filters_closed_and_handles_missing(
        self, full_custom_graph: WeightedDirectedGraph
    ) -> None:
        assert full_custom_graph.get_neighbors("A") == ["B"]
        assert full_custom_graph.get_neighbors("B") == ["A", "C"]
        assert full_custom_graph.get_neighbors("C") == []
        assert full_custom_graph.get_neighbors("D") == []
        assert full_custom_graph.get_neighbors("UNKNOWN") == []


# -------- OPERATORS --------


class TestDunderMethods:
    def test_getitem_node_and_edge(
        self, full_custom_graph: WeightedDirectedGraph
    ) -> None:
        assert full_custom_graph["A"] == {"B": (5, True), "C": (10, False)}
        assert full_custom_graph["A", "B"] == (5, True)
        assert full_custom_graph["A", "C"] == (10, False)

        with pytest.raises(KeyError):
            _ = full_custom_graph["UNKNOWN"]

        with pytest.raises(KeyError):
            _ = full_custom_graph["A", "D"]

        with pytest.raises(KeyError):
            _ = full_custom_graph["UNKNOWN", "A"]

    def test_contains_node_and_edge(
        self, full_custom_graph: WeightedDirectedGraph
    ) -> None:
        assert "A" in full_custom_graph
        assert "D" in full_custom_graph
        assert "UNKNOWN" not in full_custom_graph

        assert ("A", "B") in full_custom_graph
        assert ("A", "C") in full_custom_graph
        assert ("A", "D") not in full_custom_graph
        assert ("UNKNOWN", "A") not in full_custom_graph


# -------- PATHFINDING --------


class TestPathfinding:
    def test_shortest_path_and_can_go_basic(
        self, linear_graph: WeightedDirectedGraph
    ) -> None:
        assert linear_graph.can_go("A", "C") is True
        assert linear_graph.shortest_path("A", "C") == ["A", "B", "C"]

        assert linear_graph.can_go("C", "A") is True
        assert linear_graph.shortest_path("C", "A") == ["C", "B", "A"]

        assert linear_graph.can_go("A", "D") is False
        assert linear_graph.shortest_path("A", "D") == []

    def test_same_source_and_target(self, linear_graph: WeightedDirectedGraph) -> None:
        assert linear_graph.shortest_path("A", "A") == ["A"]
        assert linear_graph.can_go("A", "A") is True

        assert linear_graph.shortest_path("D", "D") == ["D"]
        assert linear_graph.can_go("D", "D") is True

    def test_unknown_source_or_target(
        self, linear_graph: WeightedDirectedGraph
    ) -> None:
        assert linear_graph.shortest_path("UNKNOWN", "A") == []
        assert linear_graph.can_go("UNKNOWN", "A") is False

        assert linear_graph.shortest_path("UNKNOWN", "UNKNOWN") == []
        assert linear_graph.can_go("UNKNOWN", "UNKNOWN") is False

        assert linear_graph.shortest_path("A", "UNKNOWN") == []
        assert linear_graph.can_go("A", "UNKNOWN") is False

    def test_directed_cycles_and_unreachable_in_cycle(
        self, directed_cycle_graph: WeightedDirectedGraph
    ) -> None:
        assert directed_cycle_graph.shortest_path("A", "D") == ["A", "B", "C", "D"]
        assert directed_cycle_graph.can_go("A", "D") is True

        assert directed_cycle_graph.shortest_path("D", "A") == []
        assert directed_cycle_graph.can_go("D", "A") is False

        directed_cycle_graph.set_edge_status("C", "D", False)
        assert directed_cycle_graph.shortest_path("A", "D") == []
        assert directed_cycle_graph.can_go("A", "D") is False

    def test_shortest_path_picks_fewest_hops_and_reroutes_when_closed(self) -> None:
        graph = WeightedDirectedGraph.from_unweighted(
            {
                "A": ["B", "D"],
                "B": ["C"],
                "C": ["D"],
                "D": [],
            }
        )
        assert graph.shortest_path("A", "D") == ["A", "D"]

        graph.set_edge_status("A", "D", False)
        assert graph.shortest_path("A", "D") == ["A", "B", "C", "D"]
        assert graph.can_go("A", "D") is True

        graph.set_edge_status("B", "C", False)
        assert graph.shortest_path("A", "D") == []
        assert graph.can_go("A", "D") is False

    def test_diamond_graph_visited_deduplication(self) -> None:
        graph = WeightedDirectedGraph.from_unweighted(
            {
                "A": ["B", "C"],
                "B": ["D"],
                "C": ["D"],
                "D": ["E"],
                "E": [],
            }
        )
        path = graph.shortest_path("A", "E")
        assert path == ["A", "B", "D", "E"]
        assert graph.can_go("A", "E") is True

    def test_dynamic_graph_mutation_lifecycle(
        self, empty_graph: WeightedDirectedGraph
    ) -> None:
        for node in ("S", "M1", "M2", "T"):
            empty_graph.add_node(node)

        empty_graph.add_edge("S", "M1")
        empty_graph.add_edge("M1", "T")
        empty_graph.add_edge("S", "M2")
        empty_graph.add_edge("M2", "T")

        assert empty_graph.shortest_path("S", "T") == ["S", "M1", "T"]

        empty_graph.remove_node("M1")
        assert empty_graph.shortest_path("S", "T") == ["S", "M2", "T"]

        empty_graph.remove_edge("M2", "T")
        assert empty_graph.can_go("S", "T") is False
        assert empty_graph.shortest_path("S", "T") == []
