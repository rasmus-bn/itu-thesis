import os
from algorithms.waypoint_controller import WaypointController
from engine.environment import Environment
from engine.robot import RobotBase
from engine.robot_spec import RobotSpec
from engine.simulation import SimulationBase
import pygad
from sim_math.units import Mass
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"


def pid_simulation(solution, screen_size, caption, realtime_display) -> dict:
    sim = SimulationBase(pixels_x=screen_size[0], pixels_y=screen_size[1], enable_realtime=realtime_display, enable_display=realtime_display, time_limit_seconds=30, inputs=solution, windows_caption=caption, initial_zoom=0.5)
    env = Environment(sim)
    env.generate_waypoints(distance=100, x_count=3, y_count=3, homebase_threshold=30)
    controller = WaypointController(kp=solution[0], kd=solution[1])
    robot_spec = RobotSpec(
        meta=sim.meta,
        battery_mass=Mass.in_kg(4),
        motor_mass=Mass.in_kg(4),
    )
    robot = RobotBase(sim=sim, robot_spec=robot_spec, position=(0, 0), angle=0, controller=controller, ignore_battery=True, robot_collision=False)
    robot.color = (255, 0, 0)  # Red
    sim.add_game_object(robot)
    counters = sim.run()
    return counters


def fitness_func(instance: pygad.GA, solution, solution_idx):
    generations_completed = instance.generations_completed
    thread_count = instance.parallel_processing[1]

    SCREEN_SIZE = (200, 200)
    COLUMNS = 4

    index = solution_idx % thread_count
    x = 50 + (index % COLUMNS * (SCREEN_SIZE[0] + 50))
    y = 100 + (index // COLUMNS) * (SCREEN_SIZE[1] + 50)  # Adjust y after every 4 instances
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"
    caption = f"Gen {generations_completed} Ind {solution_idx}"

    counters = pid_simulation(solution, SCREEN_SIZE, caption, False)
    waypoints_reached = counters.get('waypoints_reached', 0)
    return waypoints_reached


def run_ga():
    gene_space = [
        {'low': 0.0, 'high': 10},  # P
        {'low': 0.0, 'high': 10}   # D
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
    pid_simulation([5.87945306, 0.22862575], (300, 300), "test_14_pygad_multi", True)
    # run_ga()
