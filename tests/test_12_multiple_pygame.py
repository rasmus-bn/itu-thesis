import multiprocessing
from dataclasses import dataclass
import pygame
import os
import time


@dataclass
class SimulationParams:
    window_position: (int, int)
    window_size: (int, int)


@dataclass
class SimulationResult:
    message: str


def run_pygame_instance(simulation_id, params: SimulationParams, SimulationResults):
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{params.window_position[0]},{params.window_position[1]}"
    pygame.init()
    screen = pygame.display.set_mode(params.window_size)
    pygame.display.set_caption(f"Simulation {simulation_id}")
    running = True
    clock = pygame.time.Clock()
    # Simulate a task by waiting for the specified duration (in seconds)
    start_time = time.time()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((0, 255, 0))
        pygame.display.update()
        clock.tick(60)
        # If simulation time is over, finish the simulation
        if time.time() - start_time >= 3:
            running = False
    pygame.quit()

    # Save the result in the shared dictionary using the simulation ID
    SimulationResults[simulation_id] = SimulationResult(message=f"Simulation {simulation_id} ran for {3} seconds.")


def main():
    multiprocessing.set_start_method("spawn")  # Required for some platforms (e.g., macOS, Windows)

    # Create a Manager to handle shared data
    with multiprocessing.Manager() as manager:
        results = manager.dict()  # Shared dictionary for results

        # Start the simulations with parameters for duration
        p1 = multiprocessing.Process(target=run_pygame_instance, args=(1, SimulationParams(window_size=(100,100), window_position=(100,100)), results))
        p2 = multiprocessing.Process(target=run_pygame_instance, args=(2, SimulationParams(window_size=(100,100), window_position=(220,100)), results))

        p1.start()
        p2.start()

        # Wait for both processes to finish
        p1.join()
        p2.join()

        # Retrieve the results from the dictionary using the simulation IDs
        print(results[1])  # Output for Simulation 1
        print(results[2])  # Output for Simulation 2


if __name__ == "__main__":
    main()
