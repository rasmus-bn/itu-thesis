from random import randint, uniform


def fitness(completed_time, time_limit, collected_mass):
    return time_limit / completed_time * collected_mass


def get_single_robot(colony_total_weight: float, number_of_agents: int, agent_motor_ratio: float):
    total_agent_weight = colony_total_weight / number_of_agents
    agent_motor_weight = total_agent_weight * agent_motor_ratio
    agent_battery_weight = total_agent_weight - agent_motor_weight
    return agent_motor_weight, agent_battery_weight


# CONSTANT PARAMETERS
COLONY_TOTAL_WEIGHT = 1_000
MAX_TO_ONE_RATIO = 5

# VARIABLE PARAMETER RANGE

# 1. Agent Count
MIN_AGENT_COUNT = 3
MAX_AGENT_COUNT = 100

# 2. Motor Ratio
MIN_MOTOR_RATIO = 1 / MAX_TO_ONE_RATIO
MAX_MOTOR_RATIO = 1 - MIN_MOTOR_RATIO

# Example colony
c1_agent_count = randint(MIN_AGENT_COUNT, MAX_AGENT_COUNT)
c1_agent_motor_ratio = uniform(MIN_MOTOR_RATIO, MAX_MOTOR_RATIO)
c1_agent_motor_weight, c1_agent_battery_weight = get_single_robot(COLONY_TOTAL_WEIGHT, c1_agent_count, c1_agent_motor_ratio)

if __name__ == "__main__":
    # print(f"[DEBUG] Colony 1:\n"
    #       f"  Agent Count: {c1_agent_count}\n"
    #       f"  Motor Ratio: {c1_agent_motor_ratio:.2f}\n"
    #       f"  Motor Weight: {c1_agent_motor_weight:.2f}\n"
    #       f"  Battery Weight: {c1_agent_battery_weight:.2f}\n"
    #       f"  Total Weight: {COLONY_TOTAL_WEIGHT}")
    print(fitness(60, 60, 3))
    print(fitness(60, 60, 5))
    print(fitness(60, 60, 7))
    print(fitness(60, 60, 10))
    print(fitness(45, 60, 10))
    print(fitness(20, 60, 10))
    print(fitness(10, 60, 10))
    print(fitness(4, 60, 10))