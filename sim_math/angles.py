import math


def normalize_angle(angle):
    """Normalize an angle to be between 0 and 2pi"""
    return angle % (2 * math.pi)


def calc_global_angle(subject_pos, target_pos):
    """Calculate the global angle from subject position to target position
    The global angle is always positive between 0 and 2pi"""
    delta_x = -(subject_pos[0] - target_pos[0])
    delta_y = -(subject_pos[1] - target_pos[1])
    atan2_angle = math.atan2(delta_y, delta_x)
    # Global angle is always positive between 0 and 2pi
    if atan2_angle >= 0:
        return atan2_angle
    return 2 * math.pi + atan2_angle


def calc_relative_angle(subject_pos, subject_angle, target_pos):
    """Calculate the relative angle from subject position to target position
    The relative angle is always between -pi and pi. Left is positive, right is negative"""
    global_angle = calc_global_angle(subject_pos, target_pos)
    adjusted_angle = global_angle - subject_angle
    #
    normalized_angle = normalize_angle(adjusted_angle)
    # Local angle should return a value between -pi and pi
    if normalized_angle > math.pi:
        return normalized_angle - 2 * math.pi
    return normalized_angle


if __name__ == "__main__":
    print("1   * pi = ", 1 * math.pi)
    print("1.5 * pi = ", 1.5 * math.pi)
    print("2   * pi = ", 2 * math.pi)
    print("-------------------")
    print(calc_global_angle((0, 0), (1, 0)))  # Right
    print(calc_global_angle((0, 0), (0, 1)))  # Up
    print(calc_global_angle((0, 0), (-1, 0)))  # Left
    print(calc_global_angle((0, 0), (0, -1)))  # Down
    print("-------------------")
    dire = math.pi / 2
    print(calc_relative_angle((0, 0), dire, (1, 0)))  # Right
    print(calc_relative_angle((0, 0), dire, (0, 1)))  # Up
    print(calc_relative_angle((0, 0), dire, (-1, 0)))  # Left
    print(calc_relative_angle((0, 0), dire, (0, -1)))  # Down
