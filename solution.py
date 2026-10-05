import sys


STAZIONI = [
    "garibaldi",
    "università",
    "municipio",
    "toledo",
    "dante",
    "museo",
    "materdei",
    "vanvitelli",
    "augusteo",
    "fuga",
    "mergellina",
    "manzoni"
]

connessioni = {
    "garibaldi": ["università"],
    "università": ["garibaldi", "municipio"],
    "municipio": ["università", "toledo"],
    "toledo": ["dante", "augusteo", "municipio"],
    "dante": ["museo", "toledo"],
    "museo": ["materdei", "dante"],
    "materdei": ["museo", "vanvitelli"],
    "vanvitelli": ["museo", "fuga"],
    "augusteo": ["toledo", "fuga"],
    "fuga": ["vanvitelli", "augusteo"],
    "mergellina": ["manzoni"],
    "manzoni": ["mergellina"]
}

def calculate_fare(amount):
    if amount <= 3: return 2
    if amount <= 5: return 1
    return 0

def calculate_total_fare(amount):
    total = 0
    for i in range(amount):
        total += calculate_fare(i + 1)
    return total

class GatesManager():

    def __init__(self):
        self.inside = {}
        self.history = {}
        self.station_history = {station: {} for station in STAZIONI}
        self.connection_status = {station: {s: True for s in connessioni[station]} for station in connessioni}


    def __can_go__(self, station1, station2) -> bool:
        if station1 not in STAZIONI or station2 not in STAZIONI:
            return False
        if station2 not in self.connection_status[station1]:
            return False
        visited = set()
        stack = [station1]
        while stack:
            current = stack.pop()
            if current == station2:
                return True
            visited.add(current)
            for neighbor in self.connection_status[current]:
                if self.connection_status[current][neighbor] and neighbor not in visited:
                    stack.append(neighbor)
        return False

    def enter(self, user, station) -> str:
        if station not in STAZIONI:
            return "ERROR unknown station"
        if self.inside.get(user, False) == True:
            return "ERROR already in"
        self.inside[user] = True
        if station not in self.station_history:
            self.station_history[station] = {}
        self.station_history[station][user] = self.station_history[station].get(user, 0) + 1
        return "OK"

    def exit(self, user, station) -> str:
        if station not in STAZIONI:
            return "ERROR unknown station"
        if self.inside.get(user, False) == False:
            return "ERROR not in"
        self.inside[user] = False
        if user not in self.history:
            self.history[user] = 0
        self.history[user] += 1
        if station not in self.station_history:
            self.station_history[station] = {}
        self.station_history[station][user] = self.station_history[station].get(user, 0) + 1
        return calculate_fare(self.history.get(user, 0))

    def pending(self) -> str:
        inside = [user for user, inside in self.inside.items() if inside == True]
        if len(inside) == 0:
            return "none"
        inside.sort() # odio sortare alfabeticamente e per chiave simultaneamente, non è ottimale, amen
        inside.sort(key=lambda x: self.history.get(x, 0))
        return " ".join(inside)

    def fare(self, user) -> str:
        return calculate_total_fare(self.history.get(user, 0))

    def regulars(self, station) -> str:
        if station not in STAZIONI:
            return "ERROR unknown station"
        regulars = self.station_history.get(station, {})
        if len(regulars) == 0:
            return "none"
        regulars = sorted(regulars.items(), key=lambda x: (-x[1], x[0]))
        return " ".join(f"{user}:{count}" for user, count in regulars)

    def closed(self, station1, station2) -> str:
        if station1 not in STAZIONI or station2 not in STAZIONI:
            return "ERROR unknown station"
        if station2 not in self.connection_status[station1]:
            return "ERROR no track"
        if not self.connection_status[station1][station2]:
            return "ERROR already closed"
        self.connection_status[station1][station2] = False
        self.connection_status[station2][station1] = False
        return "OK"

    def open(self, station1, station2) -> str:
        if station1 not in STAZIONI or station2 not in STAZIONI:
            return "ERROR unknown station"
        if station2 not in self.connection_status[station1]:
            return "ERROR no track"
        if self.connection_status[station1][station2]:
            return "ERROR not closed"
        self.connection_status[station1][station2] = True
        self.connection_status[station2][station1] = True
        return "OK"

    def reachable(self, station1, station2) -> str:
        if station1 not in STAZIONI or station2 not in STAZIONI:
            return "ERROR unknown station"
        if self.__can_go__(station1, station2):
            return "YES"
        else:
            return "NO"
    
if __name__ == "__main__":
    manager = GatesManager()

    while (line := sys.stdin.readline()) != "":
        try:
            match(line.strip().split()):
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
                    print("route")

                case []:
                    pass

                case _:
                    raise Exception()
        except Exception as e:
            print("ERROR invalid command")