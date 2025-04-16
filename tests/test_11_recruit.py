from algorithms.random_and_recruit_controller import RandomRecruitController
from engine.debug_colors import Colors
from engine.environment import Environment
from engine.robot import RobotBase
from engine.robot_spec import RobotSpec
from engine.simulation import SimulationBase
from sim_math.units import Mass


def simulation():
    # SETTINGS
    ROBOT_COUNT = 10
    RESOURCES_COUNT = 10
    RESOURCES_SIZE = 150
    # ENVIRONMENT
    sim = SimulationBase(pixels_x=200, pixels_y=200, enable_realtime=True, enable_display=True, initial_zoom=0.1)
    env = Environment(sim)
    env.generate_waypoints(distance=90, x_count=21, y_count=21, homebase_threshold=80)
    env.generate_resources(count=RESOURCES_COUNT, radius=RESOURCES_SIZE)
    for i in range(ROBOT_COUNT):
        controller = RandomRecruitController()
        robot_spec = RobotSpec(
            meta=sim.meta,
            battery_mass=Mass.in_kg(15),
            motor_mass=Mass.in_kg(1),
        )
        # print(robot_spec.get_spec_sheet())
        robot = RobotBase(
            sim=sim,
            robot_spec=robot_spec,
            position=(0.0, 0.0),
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


if __name__ == "__main__":
    simulation()