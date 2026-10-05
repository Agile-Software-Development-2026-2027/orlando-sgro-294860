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

    def enter(self, user, station) -> str:
        if station not in STAZIONI:
            return print("ERROR unknown station")
        if self.inside.get(user, False) == True:
            return "ERROR already in"
        self.inside[user] = True
        return "OK"

    def exit(self, user, station) -> str:
        if station not in STAZIONI:
            return print("ERROR unknown station")
        if user not in self.inside or not self.inside[user]:
            return "ERROR not in"
        self.inside[user] = False
        self.history[user] += 1
        return calculate_fare(self.history[user])

    def pending(self) -> str:
        inside = [user for user, inside in self.inside.items() if inside == True]
        if len(inside) == 0:
            return "none"
        return "".join(inside)

    def fare(self, user) -> str:
        return calculate_total_fare(self.history[user])

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
                    print("regulars")
    
                case ["CLOSED", station1, station2]:
                    print("closed")

                case ["OPEN", station1, station2]:
                    print("open")

                case ["REACHABLE", station1, station2]:
                    print("reachable")

                case ["ROUTE", station1, station2]:
                    print("route")

                case []:
                    pass

                case _:
                    pass
        except Exception as e:
            print("ERROR invalid command")