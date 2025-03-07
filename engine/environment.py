import random
from engine.objects import Circle, Box


class Environment:
    def __init__(self, sim):
        self.sim = sim
        self.homebase = HomeBase(sim.pixels_x//2, sim.pixels_y//2)
        self.sim.add_game_object(self.homebase)
        self.resources = []

    def get_homebase(self):
        return self.homebase

    def generate_resources(self, count):
        self.resources = []
        for _ in range(count):
            x = random.randint(0, self.sim.pixels_x)
            y = random.randint(0, self.sim.pixels_y)
            resource = Resource(x, y)
            self.resources.append(resource)
            self.sim.add_game_object(resource)


class Resource(Circle):
    def __init__(self, x, y, radius=10, color=(255, 255, 0)):
        super().__init__(x=x, y=y, radius=radius, color=color)


class HomeBase(Box):
    def __init__(self, x, y, width=75, length=75, color=(0, 255, 0)):
        super().__init__(x=x, y=y, width=width, length=length, color=color, trigger=True)
