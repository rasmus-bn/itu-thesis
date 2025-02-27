import math
import pymunk
import random
from engine.objects import Box, Circle
from engine.robot import RobotBase
from engine.simulation import SimulationBase

random.seed()


class RotatingBox(Box):
    def update(self):
        force = 100000
        self.body.apply_force_at_local_point((0, force), self.left)
        self.body.apply_force_at_local_point((0, -force), self.right)


size_x = 1280
size_y = 720

sim = SimulationBase(
    pixels_x=size_x,
    pixels_y=size_y,
    enable_realtime=False,
    enable_display=True,
)

box = Box(x=200, y=500, width=50, length=50, color=(255, 0, 0))
box2 = Box(x=230, y=550, width=25, length=25, color=(0, 255, 0))
sim.add_game_object(box)
sim.add_game_object(box2)


class RotatingRobot(RobotBase):
    def controller_update(self):
        self.set_motor_values(1, 1)


robot = RotatingRobot(
    battery_capacity=1000, motor_strength=10, position=(200, 400), angle=0
)
sim.add_game_object(robot)

circle = Circle(x=300, y=500, radius=25, color=(0, 0, 255))
sim.add_game_object(circle)


# Create 5 random robots
MAX_SIZE = 500
for _ in range(500):
    x = random.randint(0, size_x)
    y = random.randint(0, size_y)
    angle = random.uniform(0, 2 * math.pi)
    battery_capacity = random.randint(10, MAX_SIZE)
    motor_strength = random.randint(10, MAX_SIZE)
    robot = RobotBase(battery_capacity, motor_strength, position=(x, y), angle=angle)
    sim.add_game_object(robot)
    motor_left = random.uniform(-1, 1)
    motor_right = random.uniform(-1, 1)
    robot.set_motor_values(motor_left, motor_right)


# Create additional 5 random boxes
padding = 20
# for _ in range(1000):
#     x = random.randint(padding, size_x - padding)
#     y = random.randint(padding, size_y - padding)
#     width = random.randint(5, padding)
#     height = random.randint(5, padding)
#     color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
#     box = Box(x=x, y=y, width=width, height=height, color=color)
#     sim.add_game_object(box)

seg_body = pymunk.Body(body_type=pymunk.Body.STATIC)
seg = pymunk.Segment(
    seg_body,
    (0, 0),
    (size_x, 0),
    5,
)
sim.space.add(seg_body, seg)

sim.run()
