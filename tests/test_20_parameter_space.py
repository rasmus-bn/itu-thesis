from datetime import datetime
import os
from time import time

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
from algorithms.random_and_recruit_controller import RandomRecruitController
from engine.debug_colors import Colors
from engine.environment import Environment
from engine.robot import RobotBase
from engine.robot_spec import RobotSpec
from engine.simulation import SimulationBase
from evolutionary.worlds import WORLDS, WorldParams
from evolutionary.colony import COLONY_TOTAL_WEIGHT, get_single_robot, MIN_AGENT_COUNT, MAX_AGENT_COUNT, MIN_MOTOR_RATIO, MAX_MOTOR_RATIO
from sim_math.units import Mass
from random import Random
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass

# Number of variations of the same environment
ENV_COUNT = 3
# ENV_COUNT = 1

# Max duration of the simulation (in-game seconds)
# TIME_LIMIT = 60
# TIME_LIMIT = 30
# TIME_LIMIT = 5

# Whether to display the simulation and run in real-time
REALTIME_AND_DISPLAY = False

# Heatmap resolution (higher resolution -> longer simulation time)

# Step size for the agent count
AGENT_COUNT_RESOLUTION = 5
# AGENT_COUNT_RESOLUTION = 20
# AGENT_COUNT_RESOLUTION = 50
# AGENT_COUNT_RESOLUTION = 100

# Step size for the motor ratio
MOTOR_RATIO_RESOLUTION = 0.05
# MOTOR_RATIO_RESOLUTION = 0.2
# MOTOR_RATIO_RESOLUTION = 1


@dataclass
class ParameterSearchState:
    world: WorldParams
    time_limit: float
    results: dict = None
    processes: list = None
    global_start_time: float = None

    def __post_init__(self):
        if self.results is None:
            self.results = {}
        if self.processes is None:
            self.processes = []
        if self.global_start_time is None:
            self.global_start_time = time()


def simulation(colony_idx: int, robot_count: int, motor_ratio: float, screen_size: tuple[int], caption: str, realtime_display: bool, time_limit: float, state: ParameterSearchState) -> dict:
    agent_motor_weight, agent_battery_weight, other_materials_weight = get_single_robot(COLONY_TOTAL_WEIGHT, robot_count, motor_ratio)

    rand = Random(123)

    # SETTINGS
    motor_mass = Mass.in_kg(agent_motor_weight)
    battery_mass = Mass.in_kg(agent_battery_weight)
    other_materials_mass = Mass.in_kg(other_materials_weight)

    for env_id in range(ENV_COUNT):

        def run_sim(e_id: int):
            start_time = time()

            # ENVIRONMENT
            sim = SimulationBase(pixels_x=screen_size[0], pixels_y=screen_size[1], enable_realtime=realtime_display, enable_display=realtime_display, initial_zoom=0.06, time_limit_seconds=time_limit, inputs={robot_count, motor_ratio}, windows_caption=caption)
            env = Environment(sim, seed=rand.randint(0, 1000))
            env.generate_waypoints(distance=90, x_count=31, y_count=31, homebase_threshold=80, visible=False)
            env.generate_resources(count=state.world.resource_count, radius=state.world.resource_radius, min_dist=state.world.min_dist, max_dist=state.world.max_dist)
            for i in range(robot_count):
                controller = RandomRecruitController()
                robot_spec = RobotSpec(meta=sim.meta, motor_mass=motor_mass, battery_mass=battery_mass, other_materials_mass=other_materials_mass)
                # print(robot_spec.get_spec_sheet())
                robot = RobotBase(
                    sim=sim,
                    robot_spec=robot_spec,
                    position=(rand.uniform(-1, 1) * 2, rand.uniform(-1, 1) * 2),
                    angle=0,
                    controller=controller,
                    ignore_battery=True,
                    robot_collision=False,
                    debug_color=Colors.get_random_color(),
                )
                robot._comms_range = 300
                robot._light_range = 300
                sim.add_game_object(robot)

            print(f"STARTING... Idx:{colony_idx}, Env:{e_id}, Robot Count:{robot_count}, Motor Ratio:{motor_ratio}")
            counters = sim.run()

            collected_resources = counters.get("collected_resources", 0)
            completed_time = counters.get("finished_early_time", time_limit)

            # Fitness Function
            fitness = time_limit / completed_time * collected_resources

            state.results[f"{colony_idx}:{e_id}"] = {
                "colony_idx": colony_idx,
                "robot_count": robot_count,
                "motor_ratio": motor_ratio,
                "collected_resources": collected_resources,
                "completed_time": completed_time,
                "fitness": fitness,
                "measurements": counters,
            }
            gen_end_time = time()
            run_time = gen_end_time - start_time
            global_run_time = gen_end_time - state.global_start_time
            print(f"...FINISHED ({run_time:.2f}s, {global_run_time:.2f}s since program start) Idx:{colony_idx}, Env:{e_id}, Fitness:{fitness}, Collected:{collected_resources}, Time:{completed_time}, Robot Count:{robot_count}, Motor Ratio:{motor_ratio}")

            completed_simulations = len(state.results.keys())
            total_simulations = len(state.processes)
            mean_runtime = global_run_time / completed_simulations
            remaining_time = mean_runtime * (total_simulations - completed_simulations)
            print(f"[Completed {completed_simulations}/{total_simulations} simulations, estimated time remaining: {(remaining_time / 60):.2f}min.]")

        state.processes.append({"func": run_sim, "env_id": env_id})


def fitness_func(robot_count: int, motor_ratio: float, thread_count: int, colony_idx: int, state: ParameterSearchState):
    # Window adjustment
    SCREEN_SIZE = (1000, 1000)
    COLUMNS = 4
    display_index = colony_idx % thread_count
    x = 50 + (display_index % COLUMNS * (SCREEN_SIZE[0] + 50))
    y = 100 + (display_index // COLUMNS) * (SCREEN_SIZE[1] + 50)  # Adjust y after every 4 instances
    os.environ["SDL_VIDEO_WINDOW_POS"] = f"{x},{y}"
    caption = f"RC:{robot_count} MR:{motor_ratio}"

    simulation(colony_idx=colony_idx, robot_count=robot_count, motor_ratio=motor_ratio, screen_size=SCREEN_SIZE, caption=caption, realtime_display=REALTIME_AND_DISPLAY, time_limit=state.time_limit, state=state)


def run_parameter_search(world: WorldParams, time_limit: float, files_prefix: str):
    state = ParameterSearchState(world=world, time_limit=time_limit)

    agent_count_range = [value for value in range(MIN_AGENT_COUNT, MAX_AGENT_COUNT + 1, AGENT_COUNT_RESOLUTION)]
    if MAX_AGENT_COUNT not in agent_count_range:
        agent_count_range.append(MAX_AGENT_COUNT)

    motor_ratio_range = []
    motor_ratio_range = np.arange(MIN_MOTOR_RATIO, MAX_MOTOR_RATIO, MOTOR_RATIO_RESOLUTION).tolist()
    motor_ratio_range = [round(x, 2) for x in motor_ratio_range]
    if MAX_MOTOR_RATIO not in motor_ratio_range:
        motor_ratio_range.append(MAX_MOTOR_RATIO)

    sim_idx = 0
    cpu_count = os.cpu_count()
    print(f"Number of CPU cores: {cpu_count}")
    thread_count = cpu_count

    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        colony_idx = []
        for robot_count in agent_count_range:
            for motor_ratio in motor_ratio_range:
                fitness_func(robot_count=robot_count, motor_ratio=motor_ratio, thread_count=thread_count, colony_idx=sim_idx, state=state)
                colony_idx.append(sim_idx)
                sim_idx += 1

        print(f"Submitting {len(state.processes)} simulations to thread pool of {thread_count} workers.")
        futures = [executor.submit(process["func"], process["env_id"]) for process in state.processes]

        for future in futures:
            future.result()

    print("All simulations completed.")

    # 2D array for the heatmap
    data = np.zeros((len(motor_ratio_range), len(agent_count_range)))

    for idx in colony_idx:
        robot_count = state.results[f"{idx}:{0}"]["robot_count"]
        robot_count_index = agent_count_range.index(robot_count)
        motor_ratio = state.results[f"{idx}:{0}"]["motor_ratio"]
        motor_ratio_index = motor_ratio_range.index(motor_ratio)
        fitnesses = [state.results[f"{idx}:{env_id}"]["fitness"] for env_id in range(ENV_COUNT)]

        mean_fitness = sum(fitnesses) / len(fitnesses)
        data[motor_ratio_index][robot_count_index] = mean_fitness

    end_time = time()
    run_time = end_time - state.global_start_time
    print(f"Total time taken: {(run_time / 60):.2f}min to run {len(state.processes)} simulations.")
    print(f"Mean execution time per simulation: {run_time / len(state.processes):.2f} seconds.")

    files_suffix = f"world-{state.world.id}_start-{int(state.global_start_time * 1000)}_end-{int(end_time * 1000)}"

    print("Saving raw data...")
    raw_file_name = f"{files_prefix}_raw_{files_suffix}.npy"
    np.save(file=raw_file_name, arr=state.results)
    print(f"Raw data saved as {raw_file_name}.")

    print("Generating heatmap...")
    plt.figure(figsize=(16, 8), dpi=80)  # Increase the figure size for a bigger output image
    plt.imshow(data, cmap="hot", origin="lower")
    plt.yticks(ticks=range(len(motor_ratio_range)), labels=motor_ratio_range)
    plt.xticks(ticks=range(len(agent_count_range)), labels=agent_count_range)
    plt.colorbar()

    # Add text annotations for each cell
    for i in range(len(motor_ratio_range)):
        for j in range(len(agent_count_range)):
            plt.text(j, i, f"{data[i, j]:.2f}", ha="center", va="center", color="white" if data[i, j] < np.max(data) / 2 else "black")

    file_name = f"{files_prefix}_heatmap_{files_suffix}.png"
    plt.savefig(file_name)
    plt.close()
    print(f"Heatmap saved as {file_name}.")


def run(files_prefix: str, test: str = None):
    time_limit = 60

    # Test mode
    if test:
        global ENV_COUNT
        global AGENT_COUNT_RESOLUTION
        global MOTOR_RATIO_RESOLUTION
        time_limit = 10
        ENV_COUNT = 1
        AGENT_COUNT_RESOLUTION = 100
        MOTOR_RATIO_RESOLUTION = 1

    for world in WORLDS:
        print("==================================================")
        print(f"Testing world: {str(world.id)} Resource Count:{world.resource_count} Resource Size:{world.resource_radius}")
        run_parameter_search(world=world, time_limit=time_limit, files_prefix=files_prefix)
        print(f"Finished testing world: {str(world.id)} Resource Count:{world.resource_count} Resource Size:{world.resource_radius}")
        print("==================================================")


if __name__ == "__main__":
    job_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    time_limit = 10
    ENV_COUNT = 1
    AGENT_COUNT_RESOLUTION = 100
    MOTOR_RATIO_RESOLUTION = 1
    run(job_id, test=False)
