import random
from engine.objects import Circle, Box


class Environment:
    def __init__(self, sim):
        self.sim = sim
        self.homebase = HomeBase(sim.pixels_x // 2, sim.pixels_y // 2)
        self.sim.add_game_object(self.homebase)
        self.resources = []
        self.collected_count = 0

        # Register collision handler for HomeBase (1) and Resource (2)
        handler = self.sim.space.add_collision_handler(1, 2)
        handler.begin = lambda arbiter, space, data: self.handle_homebase_collision(arbiter, space)

    def get_homebase(self):
        return self.homebase

    def generate_resources(self, count, radius=30):
        self.resources = []
        for _ in range(count):
            x = random.randint(0, self.sim.pixels_x)
            y = random.randint(0, self.sim.pixels_y)
            resource = Resource(x, y, radius)
            self.resources.append(resource)
            self.sim.add_game_object(resource)

    def collect_resource(self, resource):
        self.resources.remove(resource)
        self.collected_count += 1
        print(f"Collecting resource {resource}, number {self.collected_count}", )

    def handle_homebase_collision(self, arbiter, space):
        homebase_shape, resource_shape = arbiter.shapes  # Get colliding shapes

        # Find the resource object that matches the shape
        resource: Resource = next((r for r in self.resources if r.shape == resource_shape), None)

        if resource:
            self.collect_resource(resource)
            resource.delete_all_constraints()
            self.sim.remove_game_object(resource)
        else:
            print("error: cannot find resource", resource)

        return False


class Resource(Circle):
    def __init__(self, x, y, radius=10, color=(255, 255, 0)):
        self.constraints = []
        super().__init__(x=x, y=y, radius=radius, color=color)
        self.shape.collision_type = 2  # Set collision type for resource

    def on_constraint_added(self, constraint):
        self.constraints.append(constraint)

    def on_constraint_removed(self, constraint):
        self.constraints.remove(constraint)

    def delete_all_constraints(self):
        for constraint in self.constraints:
            constraint.destroy()


class HomeBase(Box):
    def __init__(self, x, y, width=75, length=75, color=(0, 255, 0)):
        super().__init__(x=x, y=y, width=width, length=length, color=color, trigger=True)
        self.shape.collision_type = 1  # Set collision type for homebase
