import random
import pymunk
import math
from engine.objects import Circle, Box
from engine.types import IWaypointData
from typing import TYPE_CHECKING
if TYPE_CHECKING: from engine.simulation import SimulationBase


class Environment:
    def __init__(self, sim):
        self.waypoint_distance = None
        self.waypointData: list[IWaypointData] = []
        self.waypoints = None
        self.sim: SimulationBase= sim
        self.homebase = HomeBase(0, 0)
        self.sim.add_game_object(self.homebase)
        self.resources = []
        self.resources_generated_count = 0
        self.collected_count = 0

        # Register collision handler for HomeBase (1) and Resource (2)
        handler = self.sim.space.add_collision_handler(1, 2)
        handler.begin = lambda arbiter, space, data: self.handle_homebase_collision(arbiter, space)

        # Give sim a back reference
        self.sim.set_environment(self)

    def get_homebase(self):
        return self.homebase

    def generate_resources(self, count, min_dist=500, max_dist=1000, radius=30, color=(255, 0, 0)):
        self.resources_generated_count = count
        self.resources = []
        for _ in range(count):
            distance = random.randint(min_dist, max_dist)
            angle = random.uniform(0, 2 * math.pi)
            x = distance * math.cos(angle)
            y = distance * math.sin(angle)
            resource = Resource(x, y, radius, color)
            self.resources.append(resource)
            self.sim.add_game_object(resource)

    def generate_waypoints(self, distance=10, x_count=5, y_count=5, homebase_threshold=50, visible=True):
        self.waypoint_distance = distance
        self.waypoints = []
        self.waypointData = []
        i = 0
        waypoint_map = {}  # Dictionary to store waypoints by their grid position

        for grid_x in range(x_count):
            for grid_y in range(y_count):
                x = -((distance * (x_count-1)) / 2) + grid_x * distance
                y = -((distance * (y_count-1)) / 2) + grid_y * distance
                waypoint = Waypoint(x, y, homebase_position=self.homebase.body.position, homebase_threshold=homebase_threshold, visible=visible)
                waypointData = IWaypointData(position=waypoint.body.position, id=i, neighbors={}, is_homebase=waypoint.is_homebase)
                self.waypointData.append(waypointData)

                waypoint_map[(grid_x, grid_y)] = waypointData

                i += 1
                self.waypoints.append(waypoint)
                self.sim.add_game_object(waypoint)

        # Assign neighbors
        for grid_x in range(x_count):
            for grid_y in range(y_count):
                waypointData = waypoint_map[(grid_x, grid_y)]
                neighbors = {
                    "up": waypoint_map.get((grid_x, grid_y + 1)),
                    "down": waypoint_map.get((grid_x, grid_y - 1)),
                    "left": waypoint_map.get((grid_x - 1, grid_y)),
                    "right": waypoint_map.get((grid_x + 1, grid_y))
                }
                # Remove None values (out of bounds neighbors)
                # waypointData.neighbors = {k: v for k, v in neighbors.items() if v is not None}
                waypointData.neighbors = neighbors

    def get_all_waypoints(self) -> list[IWaypointData]:
        return self.waypointData

    def get_waypoints_dict(self) -> dict[str, IWaypointData]:
        waypoint_dict = {}
        for waypoint in self.waypointData:
            waypoint_dict[waypoint.id] = waypoint
        return waypoint_dict

    def get_waypoint_distance(self) -> float:
        return self.waypoint_distance

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
            self.sim.increment_counter("collected_resources")
            if self.collected_count >= self.resources_generated_count:
                self.sim.set_counter("finished_early_time", self.sim.get_time_running())
                self.sim.safe_quit()  # todo: check if this works? maybe this is not the right way to quit the thread

        else:
            print("error: cannot find resource", resource)

        return False


class Waypoint(Circle):
    def __init__(self, x, y, radius=5, color=(40, 40, 40), homebase_position=(0, 0), homebase_threshold=50, visible=True):
        super().__init__(x=x, y=y, radius=radius, color=color)
        self.shape.sensor = True
        self.is_homebase = False
        self.visible = visible
        distance_to_homebase = self.body.position.get_distance(homebase_position)
        if distance_to_homebase < homebase_threshold:
            self.color = (255, 255, 255)
            self.is_homebase = True

    def draw(self, surface):
        if self.visible:
            super().draw(surface)


class Resource(Circle):
    def __init__(self, x, y, radius=10, color=(80, 80, 80)):
        self.constraints = []
        super().__init__(x=x, y=y, radius=radius, color=color)
        self.shape.collision_type = 2  # Set collision type for resource

        self.shape.filter = pymunk.ShapeFilter(
            categories=0b0100,  # This object is a resource
            mask=0b0001 | 0b0010 | 0b0100,  # Detects robots, obstacles, and goals
            group=0
        )


class HomeBase(Box):
    def __init__(self, x, y, width=200, length=200, color=(80, 80, 80)):
        super().__init__(x=x, y=y, width=width, length=length, color=color, trigger=True)
        self.shape.collision_type = 1  # Set collision type for homebase
