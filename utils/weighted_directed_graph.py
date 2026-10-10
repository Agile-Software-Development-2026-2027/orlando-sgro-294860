# pylint: disable=missing-function-docstring missing-module-docstring missing-class-docstring
# I really did not want to make this class because I did not want to break the "rule" of
#   "not overengiineering stuff"
# Based on SCRUM it was stated taht teh deadline helps to avoid adding useless stuff
#   to teh code and ship it when it is good enough,
# Apparently we had too much time in out deadline so I added this for a couple of reasons:
# 1. I really wanted to have a nicely implemented graph ro decouple it from the GatesManager
# 2. I did not really like how teh data srructure for the graph was implented in the GatesManager
# 3. This woudl help me understand how to impleemtn lint/test on github action for different files,
#   and update teh tests when changes occour
# Possible extensions:
# Currently we have a Number for teh wight and a boolean for the connection status
#   this could be easily extended to have a Callable for those fields so that can be used
#   to dinalically decide wight and status, this would work based on metadata taht we shoudl
#   attach to nodes or edges, (None by default) this way we could have "this conenction goes
#   over a bridge taht is cloded between 20:00 and 22:00" teh function would then check the
#   metadata to see if any relevant and return teh correct value

from collections import deque
from collections.abc import Iterable
from typing import Self


class WeightedDirectedGraph:
    def __init__(self, adj: dict[str, dict[str, tuple[int, bool]]]):
        # I hate python, not having proper protected types alongside everything else is urting
        #   but it is too late to rewrite everything in kotlin
        self._adj = adj

    # Iterable allows for lists, sets, tuples, etc.
    # Having a butload of options to inizialize it mandatory because I want to be able to
    #   directly define different types of graph from the start (for ease of use)
    # I wanted to do this with multiple constructors but python does not support that natively so...

    @classmethod
    def from_unweighted(cls, edges: dict[str, Iterable[str]]) -> Self:
        """{'A': ['B', 'C']} -> weight 1, open by default."""
        adj = {
            src: {dst: (1, True) for dst in neighbors}
            for src, neighbors in edges.items()
        }
        return cls(adj)

    @classmethod
    def from_weighted(cls, edges: dict[str, Iterable[tuple[str, int]]]) -> Self:
        """{'A': [('B', 5)]} -> open by default."""
        adj = {
            src: {dst: (weight, True) for dst, weight in neighbors}
            for src, neighbors in edges.items()
        }
        return cls(adj)

    @classmethod
    def from_conditional(cls, edges: dict[str, Iterable[tuple[str, bool]]]) -> Self:
        """{'A': [('B', False)]} -> weight 1 by default."""
        adj = {
            src: {dst: (1, status) for dst, status in neighbors}
            for src, neighbors in edges.items()
        }
        return cls(adj)

    @classmethod
    def from_full(cls, edges: dict[str, Iterable[tuple[str, int, bool]]]) -> Self:
        """{'A': [('B', 5, False)]}"""
        adj = {
            src: {dst: (weight, status) for dst, weight, status in neighbors}
            for src, neighbors in edges.items()
        }
        return cls(adj)

    # --- Good practices when building a proper Weighted-Directed-Graph ---

    def has_node(self, node: str) -> bool:
        return node in self._adj

    def add_node(self, node: str) -> None:
        if node not in self._adj:
            self._adj[node] = {}

    def remove_node(self, node: str) -> None:
        if node in self._adj:
            del self._adj[node]
            for neighbors in self._adj.values():
                if node in neighbors:
                    del neighbors[node]

    def has_edge(self, source: str, target: str) -> bool:
        return source in self._adj and target in self._adj[source]

    def get_edge_status(self, source: str, target: str) -> bool | None:
        if source in self._adj and target in self._adj[source]:
            _, is_open = self._adj[source][target]
            return is_open
        return None

    def get_bidirectional_edge_status(self, source: str, target: str) -> bool | None:
        # pylint: disable=arguments-out-of-order
        """
        Returns True if both edges are open, False if either is closed
        and None if either edge does not exist.
        """
        if self.has_edge(source, target) and self.has_edge(target, source):
            status1 = self.get_edge_status(source, target)
            status2 = self.get_edge_status(target, source)
            if status1 is not None and status2 is not None:
                return status1 and status2
        return None

    def had_bidirectional_edge(self, source: str, target: str) -> bool:
        # pylint: disable=arguments-out-of-order
        return self.has_edge(source, target) and self.has_edge(target, source)

    def add_edge(self, source: str, target: str):
        if source in self._adj and target in self._adj:
            self._adj[source][target] = (1, True)

    def remove_edge(self, source: str, target: str):
        if source in self._adj and target in self._adj[source]:
            del self._adj[source][target]

    def set_edge_status(self, source: str, target: str, is_open: bool):
        if source in self._adj and target in self._adj[source]:
            weight, _ = self._adj[source][target]
            self._adj[source][target] = (weight, is_open)

    def set_bidirectional_edge_status(self, source: str, target: str, is_open: bool):
        # pylint: disable=arguments-out-of-order
        self.set_edge_status(source, target, is_open)
        self.set_edge_status(target, source, is_open)

    def get_weight(self, source: str, target: str) -> int | None:
        if source in self._adj and target in self._adj[source]:
            weight, _ = self._adj[source][target]
            return weight
        return None  # No direct connection between source and target

    def set_weight(self, source: str, target: str, weight: int):
        if source in self._adj and target in self._adj[source]:
            _, is_open = self._adj[source][target]
            self._adj[source][target] = (weight, is_open)

    def get_neighbors(self, node: str) -> list[str]:
        # For what scope we can read the adj map directly from the variable... dumb python
        neighbors = self._adj.get(node)
        if not neighbors:
            return []
        return [neighbor for neighbor, (_, is_open) in neighbors.items() if is_open]

    # --- Overload ---

    def __getitem__(self, key: str | tuple[str, str]):
        if isinstance(key, tuple):
            src, dst = key
            return self._adj[src][dst]
        return self._adj[key]

    def __contains__(self, key: str | tuple[str, str]) -> bool:
        if isinstance(key, tuple):
            src, dst = key
            return src in self._adj and dst in self._adj[src]
        return key in self._adj

    # --- Used by us ---

    def can_go(self, source: str, target: str) -> bool:
        return len(self.shortest_path(source, target)) > 0

    def shortest_path(self, source: str, target: str) -> list[str]:
        if source not in self._adj:
            return []
        if source == target:
            return [source]

        queue = deque(
            [(source, [source])]
        )  # (current_node, path_to_current_node) that is indeed a lot of parentheses
        visited = {source}

        while queue:
            current_node, path = queue.popleft()
            for neighbor, (_, is_open) in self._adj[current_node].items():
                if not is_open or neighbor in visited:
                    continue
                if neighbor == target:
                    return path + [neighbor]
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

        return []


# Here ends teh Hate train against python...
#   it is a good language but it's class implementation is as bad as it gets
