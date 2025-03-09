import math
import random

from algorithms.random_search_controller import RandomSearchController
from engine.environment import Environment
from engine.robot import RobotBase
from engine.simulation import SimulationBase

# Settings
SIZE_X = 1280
SIZE_Y = 720
MAX_SIZE = 20000
ROBOT_COUNT = 5
RESOURCES_COUNT = 50

# test environment
sim = SimulationBase(pixels_x=SIZE_X, pixels_y=SIZE_Y, enable_realtime=True, enable_display=True)
env = Environment(sim)
env.generate_resources(RESOURCES_COUNT)


controller1 = RandomSearchController()
robot1 = RobotBase(10000, 10000, position=(SIZE_X//2, SIZE_Y//2), angle=2 * math.pi, controller=controller1, ignore_battery=True)
sim.add_game_object(robot1)

controller2 = RandomSearchController()
robot2 = RobotBase(10000, 10000, position=(SIZE_X//2 + 20, SIZE_Y//2), angle=2 * math.pi, controller=controller2, ignore_battery=True)
sim.add_game_object(robot2)

sim.run()