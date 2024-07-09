from enum import Enum
import matplotlib.pyplot
import random

class Material(Enum):
    IRON    = 1
    TOOLS   = 2
    WHEAT   = 3
    BREAD   = 4

class Citizen:
    pass

class Product:
    owner : Citizen = None
    price : int = 0
    def __init__(self, owner : Citizen, price : int):
        self.owner = owner
        self.price = price


class Town:
    resources : dict[Material, list[Product]] = {}
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

    def sell(self, mat: Material, amount: int, price: int, seller : Citizen):
        for i in range(amount):
            self.resources[mat].append(Product(seller, price))
        self.resources[mat].sort(key = lambda x : x.price)



class Schematic:
    input : dict[Material, int] = {}
    output : tuple[Material, int] = ()

    def __init__(
        self, input: dict[Material, int], output: tuple[Material, int]
    ) -> None:
        self.input = input
        self.output = output


class Proffession:
    name: str = None
    schematics : list[Schematic] = None

    def __init__(self, name: str):
        self.name = name
        self.schematics = []

    def add_schematic(self, schem: Schematic):
        self.schematics.append(schem)


class Citizen:
    current_schematic: Schematic = None
    money: int = 100
    proffession: Proffession = None

    def __init__(self, prof: Proffession):
        self.proffession = prof
        self.current_schematic = prof.schematics[0]

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
            new_price = town.resources[material][0].price + random.randint(-10,10)/10 if town.resources[material] else random.randint(5, 15)

            town.sell(
                self.current_schematic.output[0], self.current_schematic.output[1], new_price,self
            )


def input_prices(price_data, town : Town):
    for material in town.resources:
        if town.resources[material]:
            price_data[material].append(town.resources[material][0].price)


if __name__ == "__main__":

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

    BLACKSMITH = Proffession("Blacksmith")
    BLACKSMITH.add_schematic(Schematic({Material.IRON: 2}, (Material.TOOLS, 1)))

    FARMER = Proffession("Farmer")
    FARMER.add_schematic(Schematic({}, (Material.WHEAT, 3)))

    BAKER = Proffession("Baker")
    BAKER.add_schematic(Schematic({Material.WHEAT: 3}, (Material.BREAD, 2)))

    MINER = Proffession("Miner")
    MINER.add_schematic(Schematic({}, (Material.IRON, 3)))


    citizens : list[Citizen]= []
    citizens.append(Citizen(BAKER))
    citizens.append(Citizen(FARMER))
    citizens.append(Citizen(FARMER))
    citizens.append(Citizen(FARMER))
    citizens.append(Citizen(FARMER))
    citizens.append(Citizen(FARMER))
    citizens.append(Citizen(BLACKSMITH))
    citizens.append(Citizen(MINER))

    days = range(100)
    price_data = {
        Material.IRON: [],
        Material.BREAD: [],
        Material.TOOLS: [],
        Material.WHEAT: [],
    }


    for day in days:
        input_prices(price_data, TOWN)
        for worker in citizens:
            worker.work(town=TOWN)

    for material in price_data:
        matplotlib.pyplot.plot(days[:len(price_data[material])] , price_data[material], label = material.name)
    matplotlib.pyplot.legend()
    matplotlib.pyplot.show()
    

        


