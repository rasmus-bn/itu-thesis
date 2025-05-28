import os; os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
from random import uniform
from algorithms.random_and_recruit_controller import RandomRecruitController
from engine.environment import Environment
from engine.robot import RobotBase
from engine.robot_spec import RobotSpec
from engine.simulation import SimulationBase
from evolutionary.colony import COLONY_TOTAL_WEIGHT, get_single_robot, MIN_AGENT_COUNT, MAX_AGENT_COUNT, MIN_MOTOR_RATIO, MAX_MOTOR_RATIO
from sim_math.units import Mass
import pygad
from evolutionary.Plotter import Plotter
from evolutionary.worlds import WORLDS
from evolutionary.worlds import WorldParams


def simulation(solution, screen_size, caption, realtime_display, time_limit, world: WorldParams) -> dict:
    agent_count = int(solution[0] * 100)  # from normalized 0-1 range to count e.g. 1.0 = 100
    role_a_count_ratio = solution[1]
    role_a_robot_count = int(agent_count * role_a_count_ratio)

    # constrain to each role having at least on robot
    if role_a_robot_count < 1:
        role_a_robot_count = 1
    if role_a_robot_count >= agent_count:
        role_a_robot_count = agent_count - 1

    role_a_motor_ratio = solution[3]
    role_a_weight = solution[2] * COLONY_TOTAL_WEIGHT

    role_b_robot_count = agent_count - role_a_robot_count
    role_b_motor_ratio = solution[4]
    role_b_weight = COLONY_TOTAL_WEIGHT - role_a_weight

    role_a_agent_motor_weight, role_a_agent_battery_weight, role_a_other_materials_weight = get_single_robot(role_a_weight, role_a_robot_count, role_a_motor_ratio)
    role_b_agent_motor_weight, role_b_agent_battery_weight, role_b_other_materials_weight = get_single_robot(role_b_weight, role_b_robot_count, role_b_motor_ratio)

    # 1 robot role A
    role_a_motor_mass = Mass.in_kg(role_a_agent_motor_weight)
    role_a_battery_mass = Mass.in_kg(role_a_agent_battery_weight)
    role_a_other_materials_mass = Mass.in_kg(role_a_other_materials_weight)

    # 1 robot role B
    role_b_motor_mass = Mass.in_kg(role_b_agent_motor_weight)
    role_b_battery_mass = Mass.in_kg(role_b_agent_battery_weight)
    role_b_other_materials_mass = Mass.in_kg(role_b_other_materials_weight)

    # print(f"Role A: {role_a_robot_count} robots, Mot:{role_a_agent_motor_weight}, Bat:{role_a_agent_battery_weight}, Other:{role_a_other_materials_weight} Role Weight: {role_a_weight}")
    # print(f"Role B: {role_b_robot_count} robots, Mot:{role_b_agent_motor_weight}, Bat:{role_b_agent_battery_weight}, Other:{role_b_other_materials_weight} Role Weight: {role_b_weight}")

    # print(f"Role A:\n\tRobot Count:  {role_a_robot_count}\n\tRobot Weight: {role_a_weight/role_a_robot_count:.2f}kg\n\tMotor Ratio:  {role_a_motor_ratio:.2f}")
    # print(f"Role B:\n\tRobot Count:  {role_b_robot_count}\n\tRobot Weight: {role_b_weight/role_b_robot_count:.2f}kg\n\tMotor Ratio:  {role_b_motor_ratio:.2f}")

    # return {}  # SKIP SKIP SKIP
    # ENVIRONMENT
    RESOURCES_COUNT = world.resource_count
    RESOURCES_SIZE = world.resource_radius
    sim = SimulationBase(
        pixels_x=screen_size[0],
        pixels_y=screen_size[1],
        enable_realtime=realtime_display,
        enable_display=realtime_display,
        initial_zoom=0.5,
        time_limit_seconds=time_limit,
        inputs=solution,
        windows_caption=caption
    )
    env = Environment(sim)
    env.generate_waypoints(distance=100, x_count=31, y_count=31, homebase_threshold=80, visible=False)
    env.generate_resources(count=world.resource_count, radius=world.resource_radius, min_dist=world.min_dist, max_dist=world.max_dist, color=(0,180,0))

    def add_many_robots(robot_count, motor_mass, battery_mass, other_materials_mass, color):
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
                color=color,
                sim=sim,
                robot_spec=robot_spec,
                position=(uniform(-1, 1) * 2, uniform(-1, 1) * 2),
                angle=0,
                controller=controller,
                ignore_battery=False,
                robot_collision=False,
            )
            robot._comms_range = 300
            robot._light_range = 300
            # robot.battery.draw_debugging = True

            # Battery
            power_draw_scaler = 8     # Battery drains x times faster
            motor_force_scaler = 0.2  # Motor force is x times stronger
            robot.battery.power_draw_scaler = power_draw_scaler
            robot.motor_l.motor_force_scaler = motor_force_scaler
            robot.motor_r.motor_force_scaler = motor_force_scaler

            sim.add_game_object(robot)

    add_many_robots(role_a_robot_count, role_a_motor_mass, role_a_battery_mass, role_a_other_materials_mass, (0, 0, 255))
    add_many_robots(role_b_robot_count, role_b_motor_mass, role_b_battery_mass, role_b_other_materials_mass, (255, 0, 0))

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


def run_ga(filename:str = "test", thread_count=16, world_id: int = 0, test=None):
    filename = f"{filename}_world{world_id}"
    print(f"Running pygad with 2 roles, filename: {filename}, thread count: {thread_count} world_id: {world_id} test: {test}")
    params = WORLDS[world_id]
    plotter = Plotter(filename)

    # colony_agent_count range both included 3-100
    # role_a_count_ratio 0.0 - 1.0 both included ( already constrained by 1 robot per role requirement )
    # role_a_mass_ratio 0.01 - 0.99 both included ( 0.0 or 1.0 would make a role to have robot(s) with 0 weight )
    # role_a_motor_weight_ratio 0.01 - 0.99 both included ( 0.0 or 1.0 would make a robot without a batter or a motor )
    # role_b_motor_weight_ratio - same as role_a_motor_weight_ratio

    gene_space = [
        {'low': 0.03, 'high': 1.0},    # colony_agent_count range in normalized range 0-1 e.g. 1.0 = 100
        {'low': 0.0,  'high': 1.0},    # role_a_count_ratio 0.0 - 1.0 both included ( already constrained by 1 robot per role requirement )
        {'low': 0.01, 'high': 0.99},   # role_a_mass_ratio 0.01 - 0.99 both included ( 0.0 or 1.0 would make a role to have robot(s) with 0 weight )
        {'low': 0.01, 'high': 0.99},   # role_a_motor_weight_ratio 0.01 - 0.99 both included ( 0.0 or 1.0 would make a robot without a batter or a motor )
        {'low': 0.01, 'high': 0.99},   # role_b_motor_weight_ratio - same as role_a_motor_weight_ratio
    ]

    if test:
        ga_instance = pygad.GA(
            num_generations=1,
            num_parents_mating=1,
            fitness_func=fitness_func,
            sol_per_pop=2,
            num_genes=5,
            gene_space=gene_space,
            mutation_type="random",
            mutation_num_genes=1,
            crossover_type="uniform",
            keep_parents=1,
            parallel_processing=['process', thread_count],
            on_generation=plotter.on_generation,
            on_parents=plotter.on_parents,
        )
    else:
        ga_instance = pygad.GA(
            num_generations=30,
            num_parents_mating=10,
            fitness_func=fitness_func,
            sol_per_pop=30,
            num_genes=5,
            gene_space=gene_space,
            mutation_type="random",
            mutation_num_genes=1,
            mutation_probability=0.2,
            crossover_type="uniform",
            keep_parents=6,
            parallel_processing=['process', thread_count],
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
    print("Test 21: Evaluating colonies with different roles\n")


    # colony_agent_count range both included 3-100
    # role_a_count_ratio 0.0 - 1.0 both included ( already constrained by 1 robot per role requirement )
    # role_a_mass_ratio 0.01 - 0.99 both included ( 0.0 or 1.0 would make a role to have robot(s) with 0 weight )
    # role_a_motor_weight_ratio 0.01 - 0.99 both included ( 0.0 or 1.0 would make a robot without a batter or a motor )
    # role_b_motor_weight_ratio - same as role_a_motor_weight_ratio

    # don't forget to change the world up
    # sol = [0.5, 0.0, 0.01, 0.2, 0.2]  # colony_agent_count, role_a_count_ratio, role_a_mass_ratio, role_a_motor_weight_ratio, role_b_motor_weight_ratio
    WORLD_ID = 0
    while WORLD_ID < 5:
        worldParams = WORLDS[WORLD_ID]
        sols = [
            [0.445, 0.019, 0.851, 0.142, 0.105],
            [0.952, 0.142, 0.526, 0.304, 0.165],
            [0.801, 0.251, 0.503, 0.634, 0.429],
            [0.818, 0.612, 0.847, 0.435, 0.952],
            [0.916, 0.685, 0.836, 0.204, 0.106],
        ]
        sol = sols[WORLD_ID]

        # print(f"### ### Environment Type {WORLD_ID} ### ### ")
        # print(f"Fittest Genome: \n{sol}")

        # Running simulation
        TIME_LIMIT = 60
        REALTIME_AND_DISPLAY = True
        counters = simulation(sol, (512, 512), "test_21", REALTIME_AND_DISPLAY, TIME_LIMIT, worldParams)
        collected_resources = counters.get("collected_resources", 0)
        completed_time = counters.get("finished_early_time", TIME_LIMIT)

        # Fitness Function
        fitness = TIME_LIMIT / completed_time * collected_resources
        print(f"Fitness:{fitness} Collected:{collected_resources} Time:{completed_time} Solution:[{sol}]")
        # WORLD_ID += 1
        print()


# if __name__ == "__main__":
#     print("Testing different worlds for different roles..")
#     for i in range(len(WORLDS)):
#         new_filename = f"{filename}_world_{worldParams.id}"
#         run_ga(worldParams, new_filename, test)