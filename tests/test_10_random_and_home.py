from algorithms.random_and_home_controller import RandomHomeController
from engine.environment import Environment
from engine.robot import RobotBase
from engine.simulation import SimulationBase

# Settings
SIZE_X = 1280
SIZE_Y = 720
MAX_SIZE = 20000
ROBOT_COUNT = 4
RESOURCES_COUNT = 300
RESOURCES_SIZE = 10

# test environment
sim = SimulationBase(pixels_x=SIZE_X, pixels_y=SIZE_Y, enable_realtime=True, enable_display=True)
env = Environment(sim)
# env.generate_resources(RESOURCES_COUNT, radius=RESOURCES_SIZE)
env.generate_waypoints(distance=80, x_count=7, y_count=7, homebase_threshold=50)

# Create 5 random robots
# for _ in range(ROBOT_COUNT):
#     x = random.randint(0, SIZE_X)
#     y = random.randint(0, SIZE_Y)
#     angle = random.uniform(0, 2 * math.pi)
#     # battery_capacity = random.randint(10, MAX_SIZE)
#     # motor_strength = random.randint(10, MAX_SIZE)
#     battery_capacity = MAX_SIZE // 4
#     motor_strength = MAX_SIZE // 2
#     controller = FIAController()
#     robot = RobotBase(battery_capacity, motor_strength, position=(x, y), angle=angle, controller=controller, ignore_battery=True, robot_collision=False)
#     robot.color = (255,255,255)
#     sim.add_game_object(robot)

# battery_capacity = MAX_SIZE // 4
# motor_strength = MAX_SIZE // 2
# controller = WaypointController(counter_steering=0.3)
# robot = RobotBase(battery_capacity, motor_strength, position=(0, 0), angle=0, controller=controller, ignore_battery=True, robot_collision=False)
# robot.color = (0, 0, 255)  # Blue
# sim.add_game_object(robot)
#
# battery_capacity = MAX_SIZE // 4
# motor_strength = MAX_SIZE // 2
# controller = WaypointController(counter_steering=0.2)
# robot = RobotBase(battery_capacity, motor_strength, position=(0, 0), angle=0, controller=controller, ignore_battery=True, robot_collision=False)
# robot.color = (255, 255, 255)  # White
# sim.add_game_object(robot)

battery_capacity = MAX_SIZE // 4
motor_strength = MAX_SIZE // 2
controller = RandomHomeController()
robot = RobotBase(battery_capacity, motor_strength, position=(0, 0), angle=0, controller=controller, ignore_battery=True, robot_collision=False)
robot.color = (0, 255, 0)  # Green
sim.add_game_object(robot)

battery_capacity = MAX_SIZE // 4
motor_strength = MAX_SIZE // 2
controller = RandomHomeController()
robot = RobotBase(battery_capacity, motor_strength, position=(0, 0), angle=0, controller=controller, ignore_battery=True, robot_collision=False)
robot.color = (255, 0, 0)  # Red
sim.add_game_object(robot)

sim.run()