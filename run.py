import math
import pymunk
import random
from engine.constraints import PinJoint
from engine.objects import Box, Circle
from engine.robot import RobotBase
from engine.simulation import SimulationBase
from pymunk import Vec2d

random.seed(243)


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

box = Box(x=200, y=500, width=50, length=50, color=(0, 0, 255))
box2 = Box(x=230, y=550, width=25, length=25, color=(0, 255, 0))
sim.add_game_object(box)
sim.add_game_object(box2)


class RotatingRobot(RobotBase):
    def controller_update(self):
        self.set_motor_values(1, 1)


robot = RotatingRobot(
    battery_volume=1000, motor_volume=10, position=(200, 400), angle=0
)
sim.add_game_object(robot)

circle = Circle(x=300, y=500, radius=25, color=(0, 0, 255))
sim.add_game_object(circle)

robots = []
# Create 5 random robots
MAX_SIZE = 50000
# angle = random.uniform(0, 2 * math.pi)
# motor_left = 1
# motor_right = 1
for _ in range(100):
    x = random.randint(0, size_x)
    y = random.randint(0, size_y)
    battery_capacity = random.randint(10, MAX_SIZE)
    motor_strength = random.randint(10, MAX_SIZE)
    angle = random.uniform(0, 2 * math.pi)
    motor_left = random.uniform(-1, 1)
    motor_right = random.uniform(-1, 1)
    robot = RobotBase(battery_capacity, motor_strength, position=(x, y), angle=angle)
    sim.add_game_object(robot)
    robot.set_motor_values(motor_left, motor_right)
    robots.append(robot)

r1 = robots[3]
r2 = robots[1]
r3 = robots[9]
offset = 10
offset = {
    "obj1_offset": Vec2d(float(offset), float(offset)),
    "obj2_offset": Vec2d(offset, offset),
}


def add_constraint(subject, target):
    bounds = 50
    target_offset = (random.uniform(-bounds, bounds), random.uniform(-bounds, bounds))
    sim.add_constraint(PinJoint(subject, target, obj2_offset=target_offset))


add_constraint(robots[0], box)
add_constraint(robots[2], box)
add_constraint(robots[4], box)
add_constraint(robots[6], box)
add_constraint(robots[7], box)
add_constraint(robots[8], box)
add_constraint(robots[9], box)
add_constraint(robots[10], box)


# sim.add_constraint(PinJoint(r1, box, **offset))
# sim.add_constraint(PinJoint(r2, box, **offset))
# sim.add_constraint(PinJoint(r3, box, **offset))
# sim.add_constraint(PinJoint(robots[0], box, **offset))
# sim.add_constraint(PinJoint(robots[2], box, **offset))
# sim.add_constraint(PinJoint(robots[4], box, **offset))
# sim.add_constraint(PinJoint(robots[6], box, **offset))
# sim.add_constraint(PinJoint(robots[7], box, **offset))

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
