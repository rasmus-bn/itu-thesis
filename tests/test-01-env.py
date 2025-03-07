import math
import random

from engine import environment
from engine.environment import Environment
from engine.robot import RobotBase
from engine.simulation import SimulationBase

SIZE_X = 1280
SIZE_Y = 720

sim = SimulationBase(pixels_x=SIZE_X, pixels_y=SIZE_Y, enable_realtime=False, enable_display=True)

class RotatingRobot(RobotBase):
    def controller_update(self):
        self.set_motor_values(1, 1)

# test the environment
env = Environment(sim)
env.generate_resources(5)

# add robots
MAX_SIZE = 500
for _ in range(2000):
    x = random.randint(0, SIZE_X)
    y = random.randint(0, SIZE_Y)
    angle = random.uniform(0, 2 * math.pi)
    battery_capacity = random.randint(10, MAX_SIZE)
    motor_strength = random.randint(10, MAX_SIZE)
    robot = RobotBase(battery_capacity, motor_strength, position=(x, y), angle=angle)
    sim.add_game_object(robot)
    motor_left = random.uniform(-1, 1)
    motor_right = random.uniform(-1, 1)
    robot.set_motor_values(motor_left, motor_right)

sim.run()
