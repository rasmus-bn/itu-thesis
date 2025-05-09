from random import randint, uniform


def fitness(completed_time, time_limit, collected_mass):
    return time_limit / completed_time * collected_mass


def get_single_robot(colony_total_weight: float, number_of_agents: int, agent_motor_ratio: float):
    total_agent_weight = colony_total_weight / number_of_agents

    total_component_weight = total_agent_weight * (1 - OTHER_MATERIALS)

    agent_motor_weight = total_component_weight * agent_motor_ratio
    agent_battery_weight = total_component_weight - agent_motor_weight
    other_materials_weight = total_agent_weight - total_component_weight

    return agent_motor_weight, agent_battery_weight, other_materials_weight


# CONSTANT PARAMETERS
COLONY_TOTAL_WEIGHT = 1_000
OTHER_MATERIALS = 0.8
MAX_TO_ONE_RATIO = 5

# VARIABLE PARAMETER RANGE

# 1. Agent Count
MIN_AGENT_COUNT = 3
MAX_AGENT_COUNT = 100

# 2. Motor Ratio
MIN_MOTOR_RATIO = 1 / MAX_TO_ONE_RATIO
MAX_MOTOR_RATIO = 1 - MIN_MOTOR_RATIO

if __name__ == "__main__":
    # print(f"[DEBUG] Colony 1:\n"
    #       f"  Agent Count: {c1_agent_count}\n"
    #       f"  Motor Ratio: {c1_agent_motor_ratio:.2f}\n"
    #       f"  Motor Weight: {c1_agent_motor_weight:.2f}\n"
    #       f"  Battery Weight: {c1_agent_battery_weight:.2f}\n"
    #       f"  Total Weight: {COLONY_TOTAL_WEIGHT}")
    # Example colony
    # c1_agent_count = randint(MIN_AGENT_COUNT, MAX_AGENT_COUNT)
    # c1_agent_motor_ratio = uniform(MIN_MOTOR_RATIO, MAX_MOTOR_RATIO)
    # c1_agent_motor_weight, c1_agent_battery_weight, c1_agent_other_weight = get_single_robot(COLONY_TOTAL_WEIGHT, c1_agent_count, c1_agent_motor_ratio)

    print("homogeneous colony")
    solution = [4, 0.5]  # 4 robot, 0.5 motor ratio
    robot_count = int(solution[0])
    motor_ratio = solution[1]

    agent_motor_weight, agent_battery_weight, other_materials_weight = get_single_robot(COLONY_TOTAL_WEIGHT, robot_count, motor_ratio)
    print(agent_motor_weight, agent_battery_weight, other_materials_weight)

    print("heterogeneous colony ENCODING 1")
    solution = [0.5, 2, 0.5, 2, 0.5]  # 50:50 ratio of [2 robots with 0.5] + [2 robots with 0.5 both]

    role_a_weight = solution[0] * COLONY_TOTAL_WEIGHT
    role_a_robot_count = int(solution[1])
    role_a_motor_ratio = solution[2]

    role_b_weight = (1 - solution[0]) * COLONY_TOTAL_WEIGHT
    role_b_robot_count = int(solution[3])
    role_b_motor_ratio = solution[4]

    role_a_agent_motor_weight, role_a_agent_battery_weight, role_a_other_materials_weight = get_single_robot(role_a_weight, role_a_robot_count, role_a_motor_ratio)
    role_b_agent_motor_weight, role_b_agent_battery_weight, role_b_other_materials_weight = get_single_robot(role_b_weight, role_b_robot_count, role_b_motor_ratio)

    print(role_a_agent_motor_weight, role_a_agent_battery_weight, role_a_other_materials_weight)
    print(role_b_agent_motor_weight, role_b_agent_battery_weight, role_b_other_materials_weight)

    # print("heterogeneous colony ENCODING 2")
    # solution = [10, 0.1, 0.25, 0.5, 0.5]  # colony_agent_count, role_a_count_ratio, role_a_mass_ratio, role_a_motor_weight_ratio
    # # 4 robots, distributed in 0.25 ratio -> 1A 3B, role A should have 0.25 of the total mass,
    #
    # agent_count = int(solution[0])
    # role_a_count_ratio = solution[1]
    # role_a_robot_count = int(agent_count * role_a_count_ratio)
    # role_a_motor_ratio = solution[3]
    # role_a_weight = solution[2] * COLONY_TOTAL_WEIGHT
    #
    # role_b_robot_count = agent_count - role_a_robot_count
    # role_b_motor_ratio = solution[4]
    # role_b_weight = COLONY_TOTAL_WEIGHT - role_a_weight
    #
    # role_a_agent_motor_weight, role_a_agent_battery_weight, role_a_other_materials_weight = get_single_robot(role_a_weight, role_a_robot_count, role_a_motor_ratio)
    # role_b_agent_motor_weight, role_b_agent_battery_weight, role_b_other_materials_weight = get_single_robot(role_b_weight, role_b_robot_count, role_b_motor_ratio)
    #
    # print(f"Role A: {role_a_robot_count} robots, Mot:{role_a_agent_motor_weight}, Bat:{role_a_agent_battery_weight}, Other:{role_a_other_materials_weight} Role Weight: {role_a_weight}")
    # print(f"Role B: {role_b_robot_count} robots, Mot:{role_b_agent_motor_weight}, Bat:{role_b_agent_battery_weight}, Other:{role_b_other_materials_weight} Role Weight: {role_b_weight}")






