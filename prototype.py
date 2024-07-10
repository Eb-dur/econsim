import matplotlib.pyplot
import random
from enum import Enum

class Material(Enum):
    IRON    = 1
    TOOLS   = 2
    WHEAT   = 3
    BREAD   = 4

FOOD = (Material.BREAD,)
FOOD_VALUES = {
    Material.BREAD : 10
}

class Citizen:
    pass


class Product:
    owner: Citizen = None
    price: int = 0

    def __init__(self, owner: Citizen, price: int):
        self.owner = owner
        self.price = price


class Town:
    resources: dict[Material, list[Product]] = {}
    name: str = None

    def __init__(self, name: str) -> None:
        self.name = name

    def buy(self, mat: Material) -> int:
        if len(self.resources[mat]) < 1:
            return 0
        else:
            product = self.resources[mat].pop(0)
            product.owner.money += product.price
            return product.price

    def sell(self, mat: Material, amount: int, price: int, seller: Citizen):
        for i in range(amount):
            self.resources[mat].append(Product(seller, price))
        self.resources[mat].sort(key=lambda x: x.price)


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
    money: int = 100
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
            new_price = (
                town.resources[material][0].price + random.randint(-10, 10) / 10
                if town.resources[material]
                else random.randint(5, 15)
            )
            if new_price <= 0:
                new_price = 0.1

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
    price_data["Citizens"].append(len(citizens))


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

TOWN.prices = {
    Material.IRON: 5.,
    Material.TOOLS: 2.,
    Material.WHEAT: 1.,
    Material.BREAD: 10.,
}

PROFFESSIONS = []

BLACKSMITH = Proffession("Blacksmith")
BLACKSMITH.add_schematic(Schematic({Material.IRON: 2}, (Material.TOOLS, 1)))
PROFFESSIONS.append(BLACKSMITH)

FARMER = Proffession("Farmer")
FARMER.add_schematic(Schematic({Material.TOOLS : 1}, (Material.WHEAT, 3)))
PROFFESSIONS.append(FARMER)

BAKER = Proffession("Baker")
BAKER.add_schematic(Schematic({Material.WHEAT: 3}, (Material.BREAD, 5)))
PROFFESSIONS.append(BAKER)

MINER = Proffession("Miner")
MINER.add_schematic(Schematic({}, (Material.IRON, 3)))
PROFFESSIONS.append(MINER)

if __name__ == "__main__":
    citizens: list[Citizen] = []
    for _ in range(100):
        citizens.append(generate_random_citizen(PROFFESSIONS))

    days = range(1000)
    price_data = {
        Material.IRON: [],
        Material.BREAD: [],
        Material.TOOLS: [],
        Material.WHEAT: [],
        "Citizens": [],
    }

    for day in days:
        input_prices(price_data, TOWN, citizens)
        for worker in citizens:
            worker.do_day(town=TOWN)
            if worker.hunger <= 0:
                citizens.remove(worker)
        if day % 10 == 0:
            citizens.append(generate_random_citizen(PROFFESSIONS))
        random.shuffle(citizens)

    for material in price_data:
        if type(material) == str:
            matplotlib.pyplot.plot(days[:len(price_data[material])] , price_data[material],label = "Citizens")
            pass
        else:
            matplotlib.pyplot.plot(
                days[: len(price_data[material])],
                price_data[material],
                label=material.name,
            )

    matplotlib.pyplot.legend()
    matplotlib.pyplot.show()
