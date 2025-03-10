import math
import random
from engine.environment import Environment
from engine.robot import RobotBase
from engine.simulation import SimulationBase

# Settings
SIZE_X = 1280
SIZE_Y = 720
MAX_SIZE = 20000
ROBOT_COUNT = 10
RESOURCES_COUNT = 50

# test environment
sim = SimulationBase(pixels_x=SIZE_X, pixels_y=SIZE_Y, enable_realtime=True, enable_display=True)
env = Environment(sim)
env.generate_resources(50)

# Create 5 random robots
for _ in range(ROBOT_COUNT):
    x = random.randint(0, SIZE_X)
    y = random.randint(0, SIZE_Y)
    angle = random.uniform(0, 2 * math.pi)
    battery_capacity = random.randint(10, MAX_SIZE)
    motor_strength = random.randint(10, MAX_SIZE)
    robot = RobotBase(battery_capacity, motor_strength, position=(x, y), angle=angle)
    sim.add_game_object(robot)
    motor_left = 1
    motor_right = 0.95
    robot.set_motor_values(motor_left, motor_right)

sim.run()
