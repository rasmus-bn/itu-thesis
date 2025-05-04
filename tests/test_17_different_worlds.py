import os; os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
from random import uniform
from algorithms.random_and_recruit_controller import RandomRecruitController
from engine.debug_colors import Colors
from engine.environment import Environment
from engine.robot import RobotBase
from engine.robot_spec import RobotSpec
from engine.simulation import SimulationBase
from evolutionary.colony import COLONY_TOTAL_WEIGHT, get_single_robot, MIN_AGENT_COUNT, MAX_AGENT_COUNT, MIN_MOTOR_RATIO, MAX_MOTOR_RATIO
from sim_math.units import Mass
import pygad
from datetime import datetime
from evolutionary.Plotter import Plotter
from evolutionary.worlds import WORLDS
from evolutionary.worlds import WorldParams

def simulation(solution, screen_size, caption, realtime_display, time_limit, world: WorldParams) -> dict:
    robot_count = int(solution[0])
    motor_ratio = solution[1]
    agent_motor_weight, agent_battery_weight, other_materials_weight = get_single_robot(COLONY_TOTAL_WEIGHT, robot_count, motor_ratio)

    # ROBOT
    motor_mass = Mass.in_kg(agent_motor_weight)
    battery_mass = Mass.in_kg(agent_battery_weight)
    other_materials_mass = Mass.in_kg(other_materials_weight)

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
    env.generate_waypoints(distance=100, x_count=31, y_count=31, homebase_threshold=80, visible=True)
    env.generate_resources(count=world.resource_count, radius=world.resource_radius, min_dist=world.min_dist, max_dist=world.max_dist)
    for i in range(robot_count):
        controller = RandomRecruitController()
        robot_spec = RobotSpec(
            meta=sim.meta,
            motor_mass=motor_mass,
            battery_mass=battery_mass,
            other_materials_mass=other_materials_mass,
        )
        # print(robot_spec.get_spec_sheet())
        robot = RobotBase(
            sim=sim,
            robot_spec=robot_spec,
            position=(uniform(-1, 1) * 2, uniform(-1, 1) * 2),
            angle=0,
            controller=controller,
            ignore_battery=False,
            robot_collision=False,
            debug_color=Colors.get_random_color(),
        )
        robot._comms_range = 300
        robot._light_range = 300

        # Battery
        power_draw_scaler = 8     # Battery drains x times faster
        motor_force_scaler = 0.2  # Motor force is x times stronger
        robot.battery.power_draw_scaler = power_draw_scaler  
        robot.motor_l.motor_force_scaler = motor_force_scaler
        robot.motor_r.motor_force_scaler = motor_force_scaler

        sim.add_game_object(robot)
    counters = sim.run()
    return counters


def fitness_func(instance: pygad.GA, solution, solution_idx):
    params = instance.params  # type: ignore
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
    TIME_LIMIT = 60
    REALTIME_AND_DISPLAY = False
    counters = simulation(solution, SCREEN_SIZE, caption, REALTIME_AND_DISPLAY, TIME_LIMIT, params)
    collected_resources = counters.get("collected_resources", 0)
    completed_time = counters.get("finished_early_time", TIME_LIMIT)

    # Fitness Function
    fitness = TIME_LIMIT / completed_time * collected_resources
    print(f"G{generations_completed}I{solution_idx} Fitness:{fitness} Collected:{collected_resources} Time:{completed_time} Solution:[{str(solution[0])}, {str(solution[1])}]")
    return fitness


def run_ga(params: WorldParams, filename: str, test=None):
    plotter = Plotter(filename)

    gene_space = [
        {'low': MIN_AGENT_COUNT, 'high': MAX_AGENT_COUNT, 'step': 1},  # Agent Count
        {'low': MIN_MOTOR_RATIO, 'high': MAX_MOTOR_RATIO}  # Motor Ratio
    ]

    if test:
        ga_instance = pygad.GA(
            num_generations=1,
            num_parents_mating=1,
            fitness_func=fitness_func,
            sol_per_pop=2,
            num_genes=2,
            gene_space=gene_space,
            mutation_type="random",
            mutation_num_genes=1,
            crossover_type="uniform",
            keep_parents=1,
            parallel_processing=['process', 16],
            on_generation=plotter.on_generation,
            on_parents=plotter.on_parents,
        )
    else:
        ga_instance = pygad.GA(
            num_generations=15,
            num_parents_mating=6,
            fitness_func=fitness_func,
            sol_per_pop=30,
            num_genes=2,
            gene_space=gene_space,
            mutation_type="random",
            mutation_num_genes=1,
            crossover_type="uniform",
            keep_parents=5,
            parallel_processing=['process', 30],
            on_generation=plotter.on_generation,
            on_parents=plotter.on_parents,
        )

    # inject parameters into pygad instance
    ga_instance.params = params
    ga_instance.summary()

    # run ga
    ga_instance.run()

    # save result
    plotter.plot_all()
    plotter.plot_all_default(ga_instance)
    plotter.save_all(ga_instance)

    # print best solution
    solution, solution_fitness, _ = ga_instance.best_solution()
    print(f"Best solution: {solution} | Best fitness: {solution_fitness}")


if __name__ == "__main__":
        print("Test 19: Evaluating different worlds")
        # worldParams = WORLDS[2]
        # run_ga(worldParams)
        # print(f"testing world: {str(worldParams.id)} Resource Count:{worldParams.resource_count} Resource Size:{worldParams.resource_radius}");
        # simulation([4, 0.25], (300, 300), "test_14_pygad_multi", True, 10, worldParams)


def run(filename: str, test=None):
    print("Running different worlds..")
    for worldParams in WORLDS:
        new_filename = f"{filename}_world_{worldParams.id}"
        run_ga(worldParams, new_filename, test)
