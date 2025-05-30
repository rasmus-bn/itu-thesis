import multiprocessing
from dataclasses import dataclass
from evolutionary.worlds import WORLDS
from tests.test_17_different_worlds import simulation as homogeneous_simulation
from tests.test_21_multiple_roles import simulation as heterogeneous_simulation
import os
import numpy as np


@dataclass
class RunConfiguration:
    worldId: int
    times: int
    sol: []
    name: str = None
    enable_role_a: bool = True
    enable_role_b: bool = True


def evaluate(configuration: RunConfiguration):
    TIME_LIMIT = 60
    REALTIME_AND_DISPLAY = False
    ENV = WORLDS[configuration.worldId]
    SCREEN_SIZE = (512, 512)
    CAPTION = "Test24"
    SOL = configuration.sol
    RA = configuration.enable_role_a
    RB = configuration.enable_role_b

    if len(configuration.sol) == 3 or len(configuration.sol) == 2:
        counters = homogeneous_simulation(SOL, SCREEN_SIZE, CAPTION, REALTIME_AND_DISPLAY, TIME_LIMIT, ENV)
    elif len(configuration.sol) == 5:
        counters = heterogeneous_simulation(SOL, SCREEN_SIZE, CAPTION, REALTIME_AND_DISPLAY, TIME_LIMIT, ENV, enable_role_a=RA, enable_role_b=RB)
    else:
        raise Exception("invalid configuration:", configuration)

    collected_resources = counters.get("collected_resources", 0)
    completed_time = counters.get("finished_early_time", TIME_LIMIT)

    # Fitness Function
    fitness = TIME_LIMIT / completed_time * collected_resources
    # print(f"Fitness:{fitness} Collected:{collected_resources} Time:{completed_time} Solution:[{SOL}]")
    return fitness


def worker(config, queue):
    result = evaluate(config)
    queue.put(result)


def run(config: RunConfiguration, thread_count: int = None):
    if not thread_count:
        thread_count = os.cpu_count()
    # print(f"Starting {thread_count} threads...")
    results = []
    queue = multiprocessing.Queue()
    total_processes = config.times

    for i in range(0, total_processes, thread_count):
        processes = []
        for ii in range(min(thread_count, total_processes - i)):
            # print("starting", i, ii, i+ii)
            p = multiprocessing.Process(target=worker, args=(config, queue))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        while not queue.empty():
            results.append(queue.get())

    return results


def print_results(fitness_values, conf):
    print(f"{conf}")
    print(f"\t{fitness_values}")
    min_fitness = np.min(fitness_values)
    max_fitness = np.max(fitness_values)
    mean_fitness = np.mean(fitness_values)
    median_fitness = np.median(fitness_values)
    std_fitness = np.std(fitness_values)

    print(f"\tMinimum fitness: {min_fitness:.2f}")
    print(f"\tMaximum fitness: {max_fitness:.2f}")
    print(f"\tMean fitness: {mean_fitness:.2f}")
    print(f"\tMedian fitness: {median_fitness:.2f}")
    print(f"\tStandard deviation: {std_fitness:.2f}")


def test_all():
    print(f"Test 24 - run all solutions\n")
    TIMES = os.cpu_count() * 1

    # homogeneous_solutions_old = [
    #     RunConfiguration(worldId=0, times=TIMES, sol=[50.0/100, 0.2, 1.0]),
    #     RunConfiguration(worldId=1, times=TIMES, sol=[98.0/100, 0.268, 1.0]),
    #     RunConfiguration(worldId=2, times=TIMES, sol=[38.0/100, 0.635, 1.0]),
    #     RunConfiguration(worldId=3, times=TIMES, sol=[32.0/100, 0.764, 1.0]),
    #     RunConfiguration(worldId=4, times=TIMES, sol=[83.0/100, 0.2, 1.0]),
    # ]

    homogeneous_solutions_new = [
        RunConfiguration(worldId=0, times=TIMES, sol=[0.803, 0.115]),
        RunConfiguration(worldId=1, times=TIMES, sol=[0.867, 0.222]),
        RunConfiguration(worldId=2, times=TIMES, sol=[0.774, 0.554]),
        RunConfiguration(worldId=3, times=TIMES, sol=[0.912, 0.438]),
        RunConfiguration(worldId=4, times=TIMES, sol=[0.999, 0.187]),
    ]

    homogeneous_solutions_3_genes = [
        RunConfiguration(worldId=0, times=TIMES, sol=[0.81, 0.076, 0.194]),
        RunConfiguration(worldId=1, times=TIMES, sol=[0.984, 0.109, 0.382]),
        RunConfiguration(worldId=2, times=TIMES, sol=[0.687, 0.696, 0.273]),
        RunConfiguration(worldId=3, times=TIMES, sol=[0.466, 0.34, 0.427]),
        RunConfiguration(worldId=4, times=TIMES, sol=[0.864, 0.152, 0.632]),
    ]

    # heterogeneous_solutions = [
    #     RunConfiguration(worldId=0, times=TIMES, sol=[0.445, 0.019, 0.851, 0.142, 0.105]),
    #     RunConfiguration(worldId=1, times=TIMES, sol=[0.952, 0.142, 0.526, 0.304, 0.165]),
    #     RunConfiguration(worldId=2, times=TIMES, sol=[0.801, 0.251, 0.503, 0.634, 0.429]),
    #     RunConfiguration(worldId=3, times=TIMES, sol=[0.818, 0.612, 0.847, 0.435, 0.952]),
    #     RunConfiguration(worldId=4, times=TIMES, sol=[0.916, 0.685, 0.836, 0.204, 0.106]),
    #     RunConfiguration(worldId=0, times=TIMES, sol=[0.889, 0.99, 0.209, 0.088, 0.185]),
    # ]

    # all_solutions = homogeneous_solutions + heterogeneous_solutions
    all_solutions = homogeneous_solutions_new + homogeneous_solutions_3_genes

    for config in all_solutions:
        res = run(config)
        print_results(res, config)


def test_without_role_a():
    print(f"Test 24 - run all solutions\n")
    TIMES = os.cpu_count() * 2

    print(f"Run both roles:")
    config = RunConfiguration(worldId=0, times=TIMES, sol=[0.889, 0.99, 0.209, 0.088, 0.185])
    res = run(config)
    print_results(res, config)

    print(f"Run without roles B")
    config = RunConfiguration(worldId=0, times=TIMES, sol=[0.889, 0.99, 0.209, 0.088, 0.185], enable_role_b=False)
    res = run(config)
    print_results(res, config)


def test_extra():
    print(f"Test 24 - run extra solutions\n")
    TIMES = os.cpu_count() * 1

    extra = [
        RunConfiguration(worldId=0, times=TIMES, sol=[0.51562171, 0.20669626]),
    ]

    all_solutions = extra

    for config in all_solutions:
        res = run(config)
        print_results(res, config)


if __name__ == '__main__':
    print(f"Test 24\n")
    conf = RunConfiguration(worldId=0, times=16, sol=[50.0/100, 0.2, 1.0])
    # conf = RunConfiguration(worldId=0, times=3, sol=[0.445, 0.019, 0.851, 0.142, 0.105])
    result = run(conf)
    print_results(result, conf)