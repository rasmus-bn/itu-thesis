import numpy as np


def closest_point_on_circle(
    subject_center: tuple[float],
    circle_center: tuple[float],
    circle_radius: float,
):
    # Vector from circle to square
    direction = np.array(subject_center) - np.array(circle_center)

    # Normalize direction vector
    if np.linalg.norm(direction) == 0:
        # If circle and square centers are the same, return an arbitrary point on the circle
        return (circle_center[0] + circle_radius, circle_center[1])

    unit_direction = direction / np.linalg.norm(direction)

    # Closest point on the circle
    closest_point = np.array(circle_center) + unit_direction * circle_radius

    return tuple(closest_point)


if __name__ == "__main__":
    # Example usage
    circle_center = (0, 0)
    circle_radius = 5
    square_center = (10, 10)

    closest_point = closest_point_on_circle(circle_center, circle_radius, square_center)
    print("Closest point on circle:", closest_point)
