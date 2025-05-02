import os;os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
from random import uniform
import pygad
from algorithms.random_and_recruit_controller import RandomRecruitController
from engine.debug_colors import Colors
from engine.environment import Environment
from engine.robot import RobotBase
from engine.robot_spec import RobotSpec
from engine.simulation import SimulationBase
from evolutionary.colony import COLONY_TOTAL_WEIGHT, get_single_robot, MIN_AGENT_COUNT, MAX_AGENT_COUNT, MIN_MOTOR_RATIO, MAX_MOTOR_RATIO
from sim_math.units import Mass


def simulation(solution, screen_size, caption, realtime_display, time_limit) -> dict:
    robot_count = int(solution[0])
    motor_ratio = solution[1]
    agent_motor_weight, agent_battery_weight, other_materials_weight = get_single_robot(COLONY_TOTAL_WEIGHT, robot_count, motor_ratio)

    # SETTINGS
    RESOURCES_COUNT = 10
    RESOURCES_SIZE = 150
    motor_mass = Mass.in_kg(agent_motor_weight)
    battery_mass = Mass.in_kg(agent_battery_weight)
    other_materials_mass = Mass.in_kg(other_materials_weight)
    # ENVIRONMENT
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
    env.generate_waypoints(distance=90, x_count=31, y_count=31, homebase_threshold=80, visible=True)
    env.generate_resources(count=RESOURCES_COUNT, radius=RESOURCES_SIZE)
    for i in range(robot_count):
        controller = RandomRecruitController()
        robot_spec = RobotSpec(
            meta=sim.meta,
            motor_mass=motor_mass,
            battery_mass=battery_mass,
            other_materials_mass=other_materials_mass
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


def fitness_func(instance: pygad.GA, solution, solution_idx):
    # Window adjustment
    generations_completed = instance.generations_completed
    thread_count = instance.parallel_processing[1]
    SCREEN_SIZE = (200, 200)
    COLUMNS = 4
    index = solution_idx % thread_count
    x = 50 + (index % COLUMNS * (SCREEN_SIZE[0] + 50))
    y = 100 + (index // COLUMNS) * (SCREEN_SIZE[1] + 50)  # Adjust y after every 4 instances
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"
    caption = f"Gen {generations_completed} Ind {solution_idx}"

    # Running simulation
    TIME_LIMIT = 30
    REALTIME_AND_DISPLAY = False
    counters = simulation(solution, SCREEN_SIZE, caption, REALTIME_AND_DISPLAY, TIME_LIMIT)
    collected_resources = counters.get("collected_resources", 0)
    completed_time = counters.get("finished_early_time", TIME_LIMIT)

    # Fitness Function
    fitness = TIME_LIMIT / completed_time * collected_resources
    print(f"G{generations_completed}I{solution_idx} Fitness:{fitness} Collected:{collected_resources} Time:{completed_time} Solution:[{str(solution[0])}, {str(solution[1])}]")
    return fitness


def on_generation(ga_instance):
    print(f"Generation = {ga_instance.generations_completed}")
    print(f"Best Fitness = {ga_instance.best_solution()}")


def run_ga():
    gene_space = [
        {'low': MIN_AGENT_COUNT, 'high': MAX_AGENT_COUNT, 'step': 1},  # Agent Count
        {'low': MIN_MOTOR_RATIO, 'high': MAX_MOTOR_RATIO}  # Motor Ratio
    ]

    ga_instance = pygad.GA(
        save_solutions=True,
        save_best_solutions=True,
        num_generations=4,
        num_parents_mating=2,
        fitness_func=fitness_func,
        sol_per_pop=8,
        num_genes=2,
        gene_space=gene_space,
        mutation_type="random",
        mutation_num_genes=2,
        crossover_type=None,
        parent_selection_type="rws",  # Roulette Wheel Selection
        keep_parents=0,
        parallel_processing=['process', 8],
        on_generation=on_generation
    )

    ga_instance.run()                     # RUN the GA process

    ga_instance.plot_fitness()            # 1. Plot Fitness over Generations
    ga_instance.plot_genes()              # 2. Plot Genes (gene values across generations)
    ga_instance.plot_new_solution_rate()  # 3. Plot New Solution Rate (how many new solutions per generation)

    solution, solution_fitness, _ = ga_instance.best_solution()
    print("Best solution:", solution)
    print("Best fitness (score):", solution_fitness)


if __name__ == "__main__":
    # Fitness = (array([81., 0.4016737]), np.float64(51.87319884726225), np.int64(0))
    # simulation([71, 0.2], (300, 300), "test_14_pygad_multi", True, 60)
    run_ga()
