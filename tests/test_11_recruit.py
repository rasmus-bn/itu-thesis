from random import uniform
from algorithms.random_and_recruit_controller import RandomRecruitController
from engine.debug_colors import Colors
from engine.environment import Environment
from engine.robot import RobotBase
from engine.simulation import SimulationBase

# Settings
SIZE_X = 1400
SIZE_Y = 950
MAX_SIZE = 20000
ROBOT_COUNT = 15
RESOURCES_COUNT = 10
RESOURCES_SIZE = 70

# test environment
sim = SimulationBase(
    pixels_x=SIZE_X, pixels_y=SIZE_Y, enable_realtime=True, enable_display=True
)
env = Environment(sim)
env.generate_resources(count=RESOURCES_COUNT, radius=RESOURCES_SIZE)
env.generate_waypoints(distance=80, x_count=15, y_count=15, homebase_threshold=50)

center = (SIZE_X // 2, SIZE_Y // 2)


for i in range(ROBOT_COUNT):
    # Generate random initial position that is a little offest from the center
    random_initial_position = (
        center[0] + uniform(-1, 1) * 50,
        center[1] + uniform(-1, 1) * 50,
    )

    battery_capacity = MAX_SIZE // 4
    motor_strength = MAX_SIZE // 2
    controller = RandomRecruitController()
    robot = RobotBase(
        battery_capacity,
        motor_strength,
        position=random_initial_position,
        angle=0,
        controller=controller,
        ignore_battery=True,
        robot_collision=False,
        debug_color=Colors.get_random_color(),
    )
    robot._comms_range = 300
    robot._light_range = 300
    sim.add_game_object(robot)

sim.run()
