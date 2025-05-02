import os;os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
from algorithms.random_and_recruit_controller import RandomRecruitController
from engine.debug_colors import Colors
from engine.environment import Environment
from engine.robot import RobotBase
from engine.robot_spec import RobotSpec
from engine.simulation import SimulationBase
from evolutionary.evolutionary_test_02 import COLONY_TOTAL_WEIGHT, get_single_robot, MIN_AGENT_COUNT, MAX_AGENT_COUNT, MIN_MOTOR_RATIO, MAX_MOTOR_RATIO
from sim_math.units import Mass
from random import Random
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import matplotlib.pyplot as plt

ENV_COUNT = 2


def simulation(colony_idx:int, robot_count:int, motor_ratio:float, screen_size:tuple[int], caption:str, realtime_display:bool, time_limit:float, results:dict, processes:list) -> dict:
    agent_motor_weight, agent_battery_weight, other_materials_weight = get_single_robot(COLONY_TOTAL_WEIGHT, robot_count, motor_ratio)

    rand = Random(123)

    # SETTINGS
    RESOURCES_COUNT = 10
    RESOURCES_SIZE = 150
    motor_mass = Mass.in_kg(agent_motor_weight)
    battery_mass = Mass.in_kg(agent_battery_weight)
    other_materials_mass = Mass.in_kg(other_materials_weight)

    for env_id in range(ENV_COUNT):

        def run_sim(e_id:int):

            # ENVIRONMENT
            sim = SimulationBase(
                pixels_x=screen_size[0],
                pixels_y=screen_size[1],
                enable_realtime=realtime_display,
                enable_display=realtime_display,
                initial_zoom=0.06,
                time_limit_seconds=time_limit,
                inputs={robot_count, motor_ratio},
                windows_caption=caption
            )
            env = Environment(sim, seed=rand.randint(0, 1000))
            env.generate_waypoints(distance=90, x_count=31, y_count=31, homebase_threshold=80, visible=False)
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

            results[f"{colony_idx}:{e_id}"] = {
                "colony_idx": colony_idx,
                "robot_count": robot_count,
                "motor_ratio": motor_ratio,
                "collected_resources": collected_resources,
                "completed_time": completed_time,
                "fitness": fitness,
                "measurements": counters,
            }
            print(f"...FINISHED Idx:{colony_idx}, Env:{e_id}, Fitness:{fitness}, Collected:{collected_resources}, Time:{completed_time}, Robot Count:{robot_count}, Motor Ratio:{motor_ratio}")
        
        processes.append({"func":run_sim, "env_id":env_id})

    


def fitness_func(robot_count:int, motor_ratio:float, thread_count:int, colony_idx:int, results:dict, processes:list):
    # Window adjustment
    SCREEN_SIZE = (1000, 1000)
    COLUMNS = 4
    display_index = colony_idx % thread_count
    x = 50 + (display_index % COLUMNS * (SCREEN_SIZE[0] + 50))
    y = 100 + (display_index // COLUMNS) * (SCREEN_SIZE[1] + 50)  # Adjust y after every 4 instances
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"
    caption = f"RC:{robot_count} MR:{motor_ratio}"

    # Running simulation
    TIME_LIMIT = 60
    TIME_LIMIT = 10
    REALTIME_AND_DISPLAY = False
    simulation(colony_idx=colony_idx, robot_count=robot_count, motor_ratio=motor_ratio, screen_size=SCREEN_SIZE, caption=caption, realtime_display=REALTIME_AND_DISPLAY, time_limit=TIME_LIMIT, results=results, processes=processes)
    # mean_measurements = {}
    # for key in measurements[0].keys():
    #     mean_measurements[key] = sum([measurement[key] for measurement in measurements]) / len(measurements)
    # collected_resources = mean_measurements.get("collected_resources", 0)
    # completed_time = mean_measurements.get("finished_early_time", TIME_LIMIT)

    # # Fitness Function
    # fitness = TIME_LIMIT / completed_time * collected_resources

    # print(f"Idx:{colony_idx}, Fitness:{fitness}, Collected:{collected_resources}, Time:{completed_time}, Robot Count:{robot_count}, Motor Ratio:{motor_ratio}")
    
    # results[colony_idx] = {
    #     "robot_count": robot_count,
    #     "motor_ratio": motor_ratio,
    #     "collected_resources": collected_resources,
    #     "completed_time": completed_time,
    #     "fitness": fitness,
    #     "measurements": measurements,
    # }



def run_parameter_search():

    agent_count_resolution = 1
    agent_count_resolution = 50
    agent_count_range = [value for value in range(MIN_AGENT_COUNT, MAX_AGENT_COUNT + 1, agent_count_resolution)]
    if MAX_AGENT_COUNT not in agent_count_range:
        agent_count_range.append(MAX_AGENT_COUNT)

    motor_ratio_resolution = 0.01
    motor_ratio_resolution = .5
    motor_ratio_range = []
    motor_ratio_value = MIN_MOTOR_RATIO
    while motor_ratio_value <= MAX_MOTOR_RATIO:
        motor_ratio_range.append(motor_ratio_value)
        motor_ratio_value += motor_ratio_resolution
    if MAX_MOTOR_RATIO not in motor_ratio_range:
        motor_ratio_range.append(MAX_MOTOR_RATIO)

    results = {}

    sim_idx = 0
    thread_count = 8

    with ThreadPoolExecutor (max_workers=thread_count) as executor:
        processes = []
        colony_idx = []
        for robot_count in agent_count_range:
            for motor_ratio in motor_ratio_range:
                fitness_func(robot_count=robot_count, motor_ratio=motor_ratio, thread_count=thread_count, colony_idx=sim_idx, results=results, processes=processes)
                colony_idx.append(sim_idx)
                sim_idx += 1

        print(f"Submitting {len(processes)} simulations to thread pool of {thread_count} workers.")
        futures = [executor.submit(process["func"], process["env_id"]) for process in processes]

        for future in futures:
            future.result()
    
    print("All simulations completed.")

    # 2D array for the heatmap
    data = np.zeros((len(agent_count_range), len(motor_ratio_range)))

    for idx in colony_idx:
        fitnesses = [results[f"{idx}:{env_id}"]['fitness'] for env_id in range(ENV_COUNT)]
        robot_count = results[f"{idx}:{0}"]['robot_count']
        robot_count_index = agent_count_range.index(robot_count)
        motor_ratio = results[f"{idx}:{0}"]['motor_ratio']
        motor_ratio_index = motor_ratio_range.index(motor_ratio)

        mean_fitness = sum(fitnesses) / len(fitnesses)
        data[robot_count_index][motor_ratio_index] = mean_fitness


    plt.imshow(data, cmap='hot', origin='lower')
    plt.xticks(ticks=range(len(agent_count_range)), labels=agent_count_range)
    plt.yticks(ticks=range(len(motor_ratio_range)), labels=motor_ratio_range)
    plt.colorbar()
    plt.savefig("heatmap.png")
    plt.close()





            # if idx in results:
            #     result = results[idx]
            #     print(f"Colony {result['colony_idx']} - Robot Count: {result['robot_count']}, Motor Ratio: {result['motor_ratio']}, Fitness: {result['fitness']}, Collected Resources: {result['collected_resources']}, Completed Time: {result['completed_time']}")
            # else:
            #     print(f"Colony {idx} - No result found.")

        


    # for robot_count in agent_count_range:
    #     for motor_ratio in motor_ratio_range:
    #         fitness_func(robot_count=robot_count, motor_ratio=motor_ratio, thread_count=thread_count, colony_idx=sim_idx, results=results)
    #         sim_idx += 1


    # # NumPy 2D data frame
    # for idx, result in results.items():
    #     (robot_count, motor_ratio, collected_resources, completed_time, fitness, measurements, colony_idx) = result.values()
    #     row = int((robot_count - MIN_AGENT_COUNT) / agent_count_resolution)
    #     col = int((motor_ratio - MIN_MOTOR_RATIO) / motor_ratio_resolution)
    #     data[row][col] = fitness
    # print("Data Frame:")
    # print(data)
    
    



if __name__ == "__main__":
    # Fitness = (array([81., 0.4016737]), np.float64(51.87319884726225), np.int64(0))
    # simulation([71, 0.2], (300, 300), "test_14_pygad_multi", True, 60)
    run_parameter_search()
