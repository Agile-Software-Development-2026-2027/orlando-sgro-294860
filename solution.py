import sys
from collections import deque
from warnings import deprecated

stazioni = [
    "garibaldi",
    "universita",
    "municipio",
    "toledo",
    "dante",
    "museo",
    "materdei",
    "vanvitelli",
    "augusteo",
    "fuga",
    "mergellina",
    "manzoni",
]

connessioni = {
    "garibaldi": ["universita"],
    "universita": ["garibaldi", "municipio"],
    "municipio": ["universita", "toledo"],
    "toledo": ["dante", "augusteo", "municipio"],
    "dante": ["museo", "toledo"],
    "museo": ["materdei", "dante"],
    "materdei": ["museo", "vanvitelli"],
    "vanvitelli": ["materdei", "fuga"],
    "augusteo": ["toledo", "fuga"],
    "fuga": ["vanvitelli", "augusteo"],
    "mergellina": ["manzoni"],
    "manzoni": ["mergellina"],
}


def calculate_fare(amount):
    if amount <= 3:
        return 2
    if amount <= 5:
        return 1
    return 0


def calculate_total_fare(amount):
    total = 0
    for i in range(amount):
        total += calculate_fare(i + 1)
    return total


class GatesManager:
    # Why __something__? I'm an advocate of keeping privat stuff that should be private, only expose what is meant to be accessed from outside.
    # I know the variables could receive __ but thy're ugly for stuff I need to use frequently
    def __init__(
        self,
        connections: dict[str, list[str]] = connessioni,
        stations: list[str] = stazioni,
    ):
        self.inside = {}
        self.history = {}
        self.stations = stations
        self.station_history = {station: {} for station in stations}
        self.connections = connections
        self.connection_status = {
            station: {s: True for s in connections[station]} for station in connections
        }

    # Me from the future, making these methods private may not have been a good idea for
    def __can_go__(self, station1, station2) -> bool:
        return len(self.__can_go_shortest_path_bfs__(station1, station2)) > 0

    def __assign_cost_recursive__(self, station, cost: dict[str, int]):
        open_connections = [
            neightbor
            for neightbor in self.connections[station]
            if self.connection_status[station][neightbor] == True
        ]
        for neighbor in open_connections:
            if cost[neighbor] > cost[station] + 1:
                cost[neighbor] = cost[station] + 1
                self.__assign_cost_recursive__(neighbor, cost)

    def __reconstruct_path__(
        self, station1, station2, cost: dict[str, int]
    ) -> list[str]:
        path = [station2]
        current = station2
        while current != station1:
            for neighbor in self.connections[current]:
                if (
                    self.connection_status[current][neighbor]
                    and neighbor not in path
                    and cost[neighbor] == cost[current] - 1
                ):
                    path.append(neighbor)
                    current = neighbor
                    break
        return path[::-1]

    def __can_go_shortest_path_bfs__(self, station1, station2) -> list[str]:
        if station1 not in self.stations or station2 not in self.stations:
            return []
        if station1 == station2:
            return [station1]

        queue = deque(
            [(station1, [station1])]
        )  # (current_node, path_to_current_node) taht is indeed a lot of parentheses
        visited = {station1}

        while queue:
            current_station, path = queue.popleft()

            for neighbor in self.connections[current_station]:
                if (
                    self.connection_status[current_station][neighbor]
                    and neighbor not in visited
                ):
                    if neighbor == station2:
                        return path + [neighbor]
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return []

    # I enjoy deprecating old code instead of deleting in some cases, I know I caould use git to get it back but still I like it
    @deprecated(
        "This method is deprecated. Use __can_go_shortest_path_bfs__ instead.",
        category=DeprecationWarning,
    )
    def __can_go_shortest_path_dijkstra__(self, station1, station2) -> list[str]:
        if station1 not in self.stations or station2 not in self.stations:
            return []
        cost = {station: 9999 for station in self.stations}
        cost[station1] = 0
        self.__assign_cost_recursive__(station1, cost)
        if cost[station2] == 9999:
            return []
        return self.__reconstruct_path__(station1, station2, cost)

    def enter(self, user, station) -> str:
        if station not in self.stations:
            return "ERROR unknown station"
        if self.inside.get(user, False) == True:
            return "ERROR already in"
        self.inside[user] = True
        if station not in self.station_history:
            self.station_history[station] = {}
        self.station_history[station][user] = (
            self.station_history[station].get(user, 0) + 1
        )
        return "OK"

    def exit(self, user, station) -> str:
        if station not in self.stations:
            return "ERROR unknown station"
        if self.inside.get(user, False) == False:
            return "ERROR not in"
        self.inside[user] = False
        if user not in self.history:
            self.history[user] = 0
        self.history[user] += 1
        if station not in self.station_history:
            self.station_history[station] = {}
        self.station_history[station][user] = (
            self.station_history[station].get(user, 0) + 1
        )
        return str(calculate_fare(self.history.get(user, 0)))

    def pending(self) -> str:
        inside = [user for user, inside in self.inside.items() if inside == True]
        if len(inside) == 0:
            return "none"
        inside.sort(key=lambda x: (self.history.get(x, 0), x[0]))
        return " ".join(inside)

    def fare(self, user) -> str:
        return str(calculate_total_fare(self.history.get(user, 0)))

    def regulars(self, station) -> str:
        if station not in self.stations:
            return "ERROR unknown station"
        regulars = self.station_history.get(station, {})
        if len(regulars) == 0:
            return "none"
        regulars = sorted(regulars.items(), key=lambda x: (-x[1], x[0]))
        return " ".join(f"{user}:{count}" for user, count in regulars)

    def closed(self, station1, station2) -> str:
        if station1 not in self.stations or station2 not in self.stations:
            return "ERROR unknown station"
        if station2 not in self.connection_status[station1]:
            return "ERROR no track"
        if not self.connection_status[station1][station2]:
            return "ERROR already closed"
        self.connection_status[station1][station2] = False
        self.connection_status[station2][station1] = False
        return "OK"

    def open(self, station1, station2) -> str:
        if station1 not in self.stations or station2 not in self.stations:
            return "ERROR unknown station"
        if station2 not in self.connection_status[station1]:
            return "ERROR no track"
        if self.connection_status[station1][station2]:
            return "ERROR not closed"
        self.connection_status[station1][station2] = True
        self.connection_status[station2][station1] = True
        return "OK"

    def reachable(self, station1, station2) -> str:
        if station1 not in self.stations or station2 not in self.stations:
            return "ERROR unknown station"
        if station1 == station2:
            return "YES"
        if self.__can_go__(station1, station2):
            return "YES"
        else:
            return "NO"

    def route(self, station1, station2) -> str:
        if station1 not in self.stations or station2 not in self.stations:
            return "ERROR unknown station"
        if station1 == station2:
            return station1
        path = self.__can_go_shortest_path_bfs__(station1, station2)
        if path:
            return " ".join(path)
        else:
            return "UNREACHABLE"


def main():
    manager = GatesManager()

    while (line := sys.stdin.readline()) != "":
        try:
            match line.strip().split():
                case ["TAPIN", user, station]:
                    print(manager.enter(user, station))

                case ["TAPOUT", user, station]:
                    print(manager.exit(user, station))

                case ["PENDING"]:
                    print(manager.pending())

                case ["FARE", user]:
                    print(manager.fare(user))

                case ["REGULARS", station]:
                    print(manager.regulars(station))

                case ["CLOSED", station1, station2]:
                    print(manager.closed(station1, station2))

                case ["OPEN", station1, station2]:
                    print(manager.open(station1, station2))

                case ["REACHABLE", station1, station2]:
                    print(manager.reachable(station1, station2))

                case ["ROUTE", station1, station2]:
                    print(manager.route(station1, station2))

                case []:
                    pass

                case _:
                    raise Exception  # noqa
        except Exception:  # noqa
            print("ERROR invalid command")


if __name__ == "__main__":
    main()
