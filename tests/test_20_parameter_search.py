import multiprocessing
import itertools
import matplotlib.pyplot as plt
import numpy as np
from evolutionary.colony import MIN_AGENT_COUNT, MAX_AGENT_COUNT, MIN_MOTOR_RATIO, MAX_MOTOR_RATIO
from tests.test_17_different_worlds import simulation
from tests.test_17_different_worlds import WORLDS
import pickle
import time

param_space = [
    {'low': MIN_AGENT_COUNT, 'high': MAX_AGENT_COUNT},  # Agent Count
    {'low': 0.01, 'high': 0.99}                         # Motor Ratio
]

MOTOR_RATIO_RESOLUTION = 0.02
AGENT_RATIO_RESOLUTION = 2

# MOTOR_RATIO_RESOLUTION = 0.5
# AGENT_RATIO_RESOLUTION = 50

def evaluate(solution, world_id: int, test = None):
    print(f"Start Solution:[{solution[0]}, {solution[1]}]", flush=True)
    start_time = time.time()
    try:
        if test:
            fitness = solution[0] * solution[1]
            return (solution[0], solution[1], fitness)
        TIME_LIMIT = 60
        REALTIME_AND_DISPLAY = False
        WORLD = WORLDS[world_id]
        counters = simulation(solution, (400, 400), str(solution), REALTIME_AND_DISPLAY, TIME_LIMIT, WORLD)
        collected_resources = counters.get("collected_resources", 0)
        completed_time = counters.get("finished_early_time", TIME_LIMIT)

        fitness = TIME_LIMIT / completed_time * collected_resources
        print(f"Fitness:{fitness} Collected:{collected_resources} Time:{completed_time} Solution:[{solution[0]}, {solution[1]}] Time:{time.time() - start_time:.2f}s", flush=True)
        return (solution[0], solution[1], fitness)
    except Exception as e:
        print(f"EXCEPTION in Solution:[{solution[0]}, {solution[1]}]: {e} Time:{time.time() - start_time:.2f}s", flush=True)
        return (solution[0], solution[1], -1)

def generate_param_grid(param_space, motor_ratio_res, agent_count_step):
    agent_count_low = param_space[0]['low']
    agent_count_high = param_space[0]['high']
    motor_ratio_low = param_space[1]['low']
    motor_ratio_high = param_space[1]['high']
    agent_counts = list(range(agent_count_low, agent_count_high + 1, agent_count_step))
    motor_ratios = [round(motor_ratio_low + i * motor_ratio_res, 10) for i in range(int((motor_ratio_high - motor_ratio_low) / motor_ratio_res) + 1)]
    return list(itertools.product(agent_counts, motor_ratios)), agent_counts, motor_ratios

def plot_heatmap(results, agent_counts, motor_ratios, filename):
    heatmap = np.full((len(agent_counts), len(motor_ratios)), np.nan)
    agent_index = {v: i for i, v in enumerate(agent_counts)}
    motor_index = {v: i for i, v in enumerate(motor_ratios)}
    for agent, motor, value in results:
        i = agent_index[agent]
        j = motor_index[round(motor, 10)]
        heatmap[i, j] = value
    plt.imshow(heatmap, origin='lower', aspect='auto', cmap='viridis', extent=[min(motor_ratios), max(motor_ratios), min(agent_counts), max(agent_counts)])
    plt.colorbar(label='Fitness')
    plt.xlabel('Motor Ratio')
    plt.ylabel('Agent Count')
    plt.title('Grid Search Fitness Heatmap')
    plt.tight_layout()
    plt.savefig(f"{filename}_heatmap.png")

def worker(solution, world_id, test, queue):
    result = evaluate(solution, world_id, test)
    queue.put(result)

def run(filename: str = "test", thread_count: int = 16, world_id: int = 0, test = None):
    print(f"thread count: {thread_count} world_id: {world_id}")
    args, agent_counts, motor_ratios = generate_param_grid(param_space, MOTOR_RATIO_RESOLUTION, AGENT_RATIO_RESOLUTION)
    print(f"Motor Ratio count: {len(motor_ratios)} Agent Count count: {len(agent_counts)} Total combinations: {len(args)}")

    results = []
    queue = multiprocessing.Queue()

    for i in range(0, len(args), thread_count):
        processes = []
        for arg in args[i:i+thread_count]:
            p = multiprocessing.Process(target=worker, args=(arg, world_id, test, queue))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        while not queue.empty():
            results.append(queue.get())

    print("FINISH, saving..", flush=True)
    with open(f"{filename}_data.pkl", "wb") as f:
        pickle.dump(results, f)
    print("make heatmap", flush=True)
    plot_heatmap(results, agent_counts, motor_ratios, filename)
    print("Done", flush=True)

if __name__ == "__main__":
    run("test", 16, world_id=1, test="test1")
