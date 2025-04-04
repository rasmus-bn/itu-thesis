import multiprocessing
from dataclasses import dataclass
import pygame
import os
import time
from random import uniform
from algorithms.random_and_recruit_controller import RandomRecruitController
from engine.debug_colors import Colors
from engine.environment import Environment
from engine.robot import RobotBase
from engine.simulation import SimulationBase


def test_simulation(screensize: (int, int)):
    ROBOT_COUNT = 10
    RESOURCES_COUNT = 5
    RESOURCES_SIZE = 100

    MAX_SIZE = 20000
    BATTERY_CAPACITY = MAX_SIZE // 4
    MOTOR_STRENGTH = MAX_SIZE // 2

    # ENVIRONMENT
    sim = SimulationBase(pixels_x=screensize[0], pixels_y=screensize[1], enable_realtime=False, enable_display=True)
    env = Environment(sim)
    env.generate_waypoints(distance=100, x_count=11, y_count=11, homebase_threshold=100)
    env.generate_resources(count=RESOURCES_COUNT, radius=RESOURCES_SIZE, min_dist=200, max_dist=500)

    for i in range(ROBOT_COUNT):
        random_initial_position = (uniform(-1, 1) * 50, uniform(-1, 1) * 50)
        controller = RandomRecruitController()
        robot = RobotBase(BATTERY_CAPACITY, MOTOR_STRENGTH, position=random_initial_position, angle=0, controller=controller, ignore_battery=True, robot_collision=False, debug_color=Colors.get_random_color())
        robot._comms_range, robot._light_range = 300, 300
        sim.add_game_object(robot)

    sim.run()


@dataclass
class SimulationParams:
    window_position: (int, int)
    window_size: (int, int)


@dataclass
class SimulationResult:
    message: str


def run_pygame_instance(simulation_id, params: SimulationParams, SimulationResults):
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{params.window_position[0]},{params.window_position[1]}"
    pygame.display.set_caption(f"Simulation {simulation_id}")

    # Run the actual simulation
    test_simulation(params.window_size)

    # Save the result in the shared dictionary using the simulation ID
    SimulationResults[simulation_id] = SimulationResult(message=f"Simulation {simulation_id} ran for {3} seconds.")


def main():
    multiprocessing.set_start_method("spawn")  # Required for some platforms (e.g., macOS, Windows)

    # Create a Manager to handle shared data
    with multiprocessing.Manager() as manager:
        results = manager.dict()  # Shared dictionary for results

        # Start the simulations with parameters for duration
        window_size = (200, 200)

        COUNT = 4
        processes = []

        for index in range(COUNT):
            x = 50 + (index%5 * (window_size[0] + 50))
            y = 100 + (index // 5) * (window_size[1] + 50)  # Adjust y after every 4 instances
            window_position = (x, y)
            process = multiprocessing.Process(
                target=run_pygame_instance,
                args=(index, SimulationParams(window_size=window_size, window_position=window_position), results)
            )
            process.start()
            processes.append(process)
            # time.sleep(0.5)  # BUGFIX: window showed behind IDE

        # Wait for both processes to finish
        for process in processes:
            process.join()

        # Retrieve the results from the dictionary
        for i in range(COUNT):
            print(results[i])


if __name__ == "__main__":
    main()