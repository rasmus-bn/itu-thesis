from dataclasses import dataclass
from typing import List
import os;os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
from random import uniform
from algorithms.random_and_recruit_controller import RandomRecruitController
from engine.debug_colors import Colors
from engine.environment import Environment
from engine.robot import RobotBase
from engine.robot_spec import RobotSpec
from engine.simulation import SimulationBase
from evolutionary.evolutionary_test_02 import COLONY_TOTAL_WEIGHT, get_single_robot, MIN_AGENT_COUNT, MAX_AGENT_COUNT, MIN_MOTOR_RATIO, MAX_MOTOR_RATIO
from sim_math.units import Mass


@dataclass
class WorldParams:
    id: int
    resource_count: int
    resource_radius: int
    min_dist: int
    max_dist: int


WORLDS: List[WorldParams] = [
    WorldParams(id=0, resource_count=50, resource_radius=10, min_dist=500, max_dist=1000),  # World 0: 200 small resources
    WorldParams(id=1, resource_count=10, resource_radius=50, min_dist=500, max_dist=1000),  # World 1: 30 medium resources
    WorldParams(id=2, resource_count=3, resource_radius=200, min_dist=500, max_dist=1000),  # World 2: 3 large resources
    WorldParams(id=3, resource_count=10, resource_radius=50, min_dist=300, max_dist=500),   # World 3: close by resources
    WorldParams(id=4, resource_count=10, resource_radius=50, min_dist=800, max_dist=1000),  # World 4: far away located resources
    WorldParams(id=5, resource_count=10, resource_radius=50, min_dist=500, max_dist=1000),  # World 5: Obstacles included
]


def simulation(solution, screen_size, caption, realtime_display, time_limit, world: WorldParams) -> dict:
    robot_count = int(solution[0])
    motor_ratio = solution[1]
    agent_motor_weight, agent_battery_weight = get_single_robot(COLONY_TOTAL_WEIGHT, robot_count, motor_ratio)

    # ROBOT
    motor_mass = Mass.in_kg(agent_motor_weight)
    battery_mass = Mass.in_kg(agent_battery_weight)

    # ENVIRONMENT
    RESOURCES_COUNT = world.resource_count
    RESOURCES_SIZE = world.resource_radius
    sim = SimulationBase(
        pixels_x=screen_size[0],
        pixels_y=screen_size[1],
        enable_realtime=realtime_display,
        enable_display=realtime_display,
        initial_zoom=0.06,
        time_limit_seconds=time_limit,
        inputs=solution,
        windows_caption=caption
    )
    env = Environment(sim)
    env.generate_waypoints(distance=90, x_count=31, y_count=31, homebase_threshold=80, visible=False)
    env.generate_resources(count=world.resource_count, radius=world.resource_radius, min_dist=world.min_dist, max_dist=world.max_dist)
    for i in range(robot_count):
        controller = RandomRecruitController()
        robot_spec = RobotSpec(
            meta=sim.meta,
            motor_mass=motor_mass,
            battery_mass=battery_mass
        )
        # print(robot_spec.get_spec_sheet())
        robot = RobotBase(
            sim=sim,
            robot_spec=robot_spec,
            position=(uniform(-1, 1) * 2, uniform(-1, 1) * 2),
            angle=0,
            controller=controller,
            ignore_battery=True,
            robot_collision=False,
            debug_color=Colors.get_random_color(),
        )
        robot._comms_range = 300
        robot._light_range = 300
        sim.add_game_object(robot)
    counters = sim.run()
    return counters


if __name__ == "__main__":
    print("Test 17: different worlds")
    for worldParams in WORLDS:
        print(f"testing world: {str(worldParams.id)} Resource Count:{worldParams.resource_count} Resource Size:{worldParams.resource_radius}");
        simulation([71, 0.2], (300, 300), "test_14_pygad_multi", True, 10, worldParams)

