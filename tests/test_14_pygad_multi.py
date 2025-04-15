import os
from algorithms.waypoint_controller import WaypointController
from engine.environment import Environment
from engine.robot import RobotBase
from engine.simulation import SimulationBase
import pygad
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"


def pid_simulation(solution, solution_id: int, thread_count: int, generations_completed: int) -> dict:
    screensize = (200, 200)
    index = solution_id % thread_count
    columns = 4
    x = 50 + (index % columns * (screensize[0] + 50))
    y = 100 + (index // columns) * (screensize[1] + 50)  # Adjust y after every 4 instances
    window_position = (x, y)
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{window_position[0]},{window_position[1]}"
    caption = f"Gen {generations_completed} Ind {solution_id}"
    sim = SimulationBase(pixels_x=screensize[0], pixels_y=screensize[1], enable_realtime=False, enable_display=True, time_limit_seconds=30, inputs=solution, windows_caption=caption, initial_zoom=0.5)
    env = Environment(sim)
    env.generate_waypoints(distance=100, x_count=3, y_count=3, homebase_threshold=30)
    controller = WaypointController(kp=solution[0], kd=solution[1])
    robot = RobotBase(5000, 10000, position=(0, 0), angle=0, controller=controller, ignore_battery=True, robot_collision=False)
    robot.color = (255, 0, 0)  # Red
    sim.add_game_object(robot)
    counters = sim.run()
    return counters


def fitness_func(instance: pygad.GA, sol, solution_idx):
    generations_completed = instance.generations_completed
    thread_count = instance.parallel_processing[1]
    counters = pid_simulation(sol, solution_idx, thread_count, generations_completed)
    waypoints_reached = counters.get('waypoints_reached', 0)
    return waypoints_reached


def run_ga():
    gene_space = [
        {'low': 0.0, 'high': 10.0},  # P
        {'low': 0.0, 'high': 10.0}  # D
    ]

    ga_instance = pygad.GA(
        num_generations=100,
        num_parents_mating=6,
        fitness_func=fitness_func,
        sol_per_pop=30,
        num_genes=2,
        gene_space=gene_space,
        mutation_type="random",
        mutation_num_genes=2,
        crossover_type="uniform",
        keep_parents=5,
        parallel_processing=['process', 10]
    )

    # RUN the GA process
    ga_instance.run()

    # Plot fitness after the run
    ga_instance.plot_fitness()
    solution, solution_fitness, _ = ga_instance.best_solution()
    print("Best solution (motor_size, battery_size):", solution)
    print("Best fitness (score):", solution_fitness)


if __name__ == "__main__":
    # pid_simulation((300,300))
    run_ga()
