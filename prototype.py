import matplotlib.pyplot
import random
import heapq
from enum import Enum


class Material(Enum):
    IRON = 1
    TOOLS = 2
    WHEAT = 3
    BREAD = 4


FOOD = (Material.BREAD,)
FOOD_VALUES = {Material.BREAD: 10}


class Citizen:
    pass


class Product:
    owner: Citizen = None
    price: int = 0

    def __init__(self, owner: Citizen, price: int):
        self.owner = owner
        self.price = price

    def __lt__(self, other: "Product") -> bool:
        return self.price < other.price

    def __le__(self, other: "Product") -> bool:
        return self.price <= other.price

    def __gt__(self, other: "Product") -> bool:
        return self.price > other.price

    def __ge__(self, other: "Product") -> bool:
        return self.price >= other.price


class Town:
    resources: dict[Material, list[Product]] = {}
    name: str = None

    def __init__(self, name: str) -> None:
        self.name = name

    def buy(self, mat: Material) -> int:
        if len(self.resources[mat]) < 1:
            return 0
        else:
            product = heapq.heappop(self.resources[mat])
            product.owner.money += product.price
            return product.price

    def sell(self, mat: Material, amount: int, price: int, seller: Citizen):
        for _ in range(amount):
            heapq.heappush(self.resources[mat], Product(seller, price))
        # self.resources[mat].sort(key=lambda x: x.price)


class Schematic:
    input: dict[Material, int] = {}
    output: tuple[Material, int] = ()

    def __init__(
        self, input: dict[Material, int], output: tuple[Material, int]
    ) -> None:
        self.input = input
        self.output = output


class Proffession:
    name: str = None
    schematics: list[Schematic] = None

    def __init__(self, name: str):
        self.name = name
        self.schematics = []

    def add_schematic(self, schem: Schematic):
        self.schematics.append(schem)


class Citizen:
    hunger = 0
    current_schematic: Schematic = None
    money: float = 1000
    proffession: Proffession = None

    def __init__(self, prof: Proffession):
        self.proffession = prof
        self.current_schematic = prof.schematics[0]

    def get_price(self, town: Town, mat: Material) -> float:
        if town.resources[mat]:
            return town.resources[mat][0].price
        else:
            return None

    def can_buy_all(self, town: Town) -> bool:
        total = 0
        for resource in self.current_schematic.input:
            if self.current_schematic.input[resource] > len(town.resources[resource]):
                return False
            for i in range(self.current_schematic.input[resource]):
                total += town.resources[resource][i].price
        return self.money >= total

    def buy(self, town: Town, mat: Material) -> None:
        cost = town.buy(mat)
        if cost != 0:
            self.money -= cost

    def work(self, town: Town):
        if self.can_buy_all(town):
            for material in self.current_schematic.input:
                for _ in range(self.current_schematic.input[material]):
                    self.buy(town, material)

            material = self.current_schematic.output[0]
            resource = town.resources[material]
            if resource:
                if resource[0].owner != self:
                    new_price = resource[0].price + random.randint(-10, 10)
                else:
                    new_price = resource[0].price
                if new_price < 10:
                    new_price = 10
            else:
                new_price = random.randint(50, 150)

            town.sell(
                self.current_schematic.output[0],
                self.current_schematic.output[1],
                new_price,
                self,
            )

    def find_food(self, town: Town):
        cheapest_food = None
        for food in FOOD:
            if town.resources[food]:
                if (
                    cheapest_food == None
                    or town.resources[food][0].price < cheapest_food
                ):
                    cheapest_food = food
        if cheapest_food:
            price = self.get_price(town, cheapest_food)
            if price and price < self.money:
                self.buy(town, food)
                self.hunger += FOOD_VALUES[food]
                if self.hunger > 100:
                    self.hunger = 0

    def do_day(self, town: Town):
        self.hunger -= 5
        if self.hunger <= 0:
            if self.hunger < 100:
                self.find_food(town)
            self.work(town)


def input_prices(price_data, town: Town, citizens):
    for material in town.resources:
        if town.resources[material]:
            price_data[material].append(town.resources[material][0].price)
        elif price_data[material]:
            price_data[material].append(price_data[material][-1])
    for proffession in PROFFESSIONS:
        price_data[proffession.name].append(sum(x.proffession.name == proffession.name for x in citizens))


def generate_random_citizen(proffessions: list[Proffession]):
    job = random.randint(0, len(proffessions) - 1)
    return Citizen(proffessions[job])


TOWN = Town("Köping")
TOWN.resources = {
    Material.IRON: [],
    Material.TOOLS: [],
    Material.WHEAT: [],
    Material.BREAD: [],
}

PROFFESSIONS = []

BLACKSMITH = Proffession("Blacksmith")
BLACKSMITH.add_schematic(Schematic({Material.IRON: 1}, (Material.TOOLS, 1)))
PROFFESSIONS.append(BLACKSMITH)

FARMER = Proffession("Farmer")
FARMER.add_schematic(Schematic({Material.TOOLS: 1}, (Material.WHEAT, 1)))
PROFFESSIONS.append(FARMER)

BAKER = Proffession("Baker")
BAKER.add_schematic(Schematic({Material.WHEAT: 1}, (Material.BREAD, 7)))
PROFFESSIONS.append(BAKER)

MINER = Proffession("Miner")
MINER.add_schematic(Schematic({}, (Material.IRON, 1)))
PROFFESSIONS.append(MINER)

if __name__ == "__main__":
    citizens: list[Citizen] = []
    citizens2: list[Citizen] = []
    for _ in range(1000):
        citizens.append(generate_random_citizen(PROFFESSIONS))

    days = range(1000)
    price_data = {
        Material.IRON: [],
        Material.BREAD: [],
        Material.TOOLS: [],
        Material.WHEAT: [],
        "Blacksmith": [],
        "Farmer" : [],
        "Baker" : [],
        "Miner" : [],
    }

    # Simulation
    for day in days:
        input_prices(price_data, TOWN, citizens)
        for _ in range(len(citizens)):
            worker = citizens[random.randint(0, len(citizens) - 1)]
            worker.do_day(town=TOWN)
            citizens.remove(worker)
            if worker.hunger > 0:
                citizens2.append(worker)
        citizens = citizens2
        citizens2 = []
        if day % 100 == 0:
            for _ in range(10):
                citizens.append(generate_random_citizen(PROFFESSIONS))
    # --------------------------------------------------------------------#
    for material in price_data:
        if type(material) == str:
            matplotlib.pyplot.plot(
                days[: len(price_data[material])],
                price_data[material],
                label=material,
                linestyle = "dashdot"
            )
            pass
        else:
            matplotlib.pyplot.plot(
                days[: len(price_data[material])],
                price_data[material],
                label=material.name,
            )

    matplotlib.pyplot.legend()
    matplotlib.pyplot.show()
