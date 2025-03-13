import random
from engine.objects import Circle, Box


class Environment:
    def __init__(self, sim):
        self.waypoints = None
        self.sim = sim
        self.homebase = HomeBase(sim.pixels_x // 2, sim.pixels_y // 2)
        self.sim.add_game_object(self.homebase)
        self.resources = []
        self.collected_count = 0

        # Register collision handler for HomeBase (1) and Resource (2)
        handler = self.sim.space.add_collision_handler(1, 2)
        handler.begin = lambda arbiter, space, data: self.handle_homebase_collision(arbiter, space)

        # Give sim a back reference
        self.sim.set_environment(self)

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

    def generate_waypoints(self, distance=10):
        self.waypoints = []
        for x in range(0, self.sim.pixels_x, distance):
            for y in range(0, self.sim.pixels_y, distance):
                waypoint = Waypoint(x, y)
                self.waypoints.append(waypoint)
                self.sim.add_game_object(waypoint)

    def handle_homebase_collision(self, arbiter, space):
        homebase_shape, resource_shape = arbiter.shapes  # Get colliding shapes

        # Find the resource object that matches the shape
        resource: Resource = next((r for r in self.resources if r.shape == resource_shape), None)

        if resource:
            # Detach the resource from all attached robots
            for constraint in resource.body.constraints:
                constraint.tether.robot.detach_from_resource()

            # Clean all references
            self.resources.remove(resource)
            self.sim.remove_game_object(resource)
            self.collected_count += 1
            print(f"Collecting resource {resource}, number {self.collected_count}", )
        else:
            print("error: cannot find resource", resource)

        return False


class Waypoint(Circle):
    def __init__(self, x, y, radius=5, color=(40, 200, 40)):
        super().__init__(x=x, y=y, radius=radius, color=color)
        self.shape.sensor = True


class Resource(Circle):
    def __init__(self, x, y, radius=10, color=(80, 80, 80)):
        self.constraints = []
        super().__init__(x=x, y=y, radius=radius, color=color)
        self.shape.collision_type = 2  # Set collision type for resource


class HomeBase(Box):
    def __init__(self, x, y, width=200, length=200, color=(30, 30, 30)):
        super().__init__(x=x, y=y, width=width, length=length, color=color, trigger=True)
        self.shape.collision_type = 1  # Set collision type for homebase
