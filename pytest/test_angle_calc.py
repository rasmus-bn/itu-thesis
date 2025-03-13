import math
import pytest
from sim_math.angles import calc_relative_angle


# Subject direction
class SubjectDir:
    RIGHT_0 = 0
    RIGHT = math.pi * 2
    UP = math.pi * 0.5
    LEFT = math.pi
    DOWN = math.pi * 1.5


class TargetPos:
    RIGHT = (1, 0)
    ABOVE = (0, 1)
    LEFT = (-1, 0)
    BELOW = (0, -1)


class ExpectedAngle:
    FRONT_OF = (0,)
    LEFT_OF = (1.57,)
    RIGHT_OF = (-1.57,)
    BEHIND_OF = (3.14, -3.14)


# Neigbour position
N_A = (0, 1)  # Neighbour above
N_R = (1, 0)  # Neighbour right
N_B = (0, -1)  # Neighbour below
N_L = (-1, 0)  # Neighbour left


test_data = [
    # Subject points up
    (
        (0, 0, SubjectDir.UP),
        N_A,
        ExpectedAngle.FRONT_OF,
        "Subject points up, neighbour is above",
    ),
    (
        (0, 0, SubjectDir.UP),
        N_R,
        ExpectedAngle.RIGHT_OF,
        "Subject points up, neighbour is right",
    ),
    (
        (0, 0, SubjectDir.UP),
        N_B,
        ExpectedAngle.BEHIND_OF,
        "Subject points up, neighbour is below",
    ),
    (
        (0, 0, SubjectDir.UP),
        N_L,
        ExpectedAngle.LEFT_OF,
        "Subject points up, neighbour is left",
    ),
    # Subject points right
    (
        (0, 0, SubjectDir.RIGHT),
        N_A,
        ExpectedAngle.LEFT_OF,
        "Subject points right, neighbour is above",
    ),
    (
        (0, 0, SubjectDir.RIGHT),
        N_R,
        ExpectedAngle.FRONT_OF,
        "Subject points right, neighbour is right",
    ),
    (
        (0, 0, SubjectDir.RIGHT),
        N_B,
        ExpectedAngle.RIGHT_OF,
        "Subject points right, neighbour is below",
    ),
    (
        (0, 0, SubjectDir.RIGHT),
        N_L,
        ExpectedAngle.BEHIND_OF,
        "Subject points right, neighbour is left",
    ),
    # Subject points right0
    (
        (0, 0, SubjectDir.RIGHT_0),
        N_A,
        ExpectedAngle.LEFT_OF,
        "Subject points right0, neighbour is above",
    ),
    (
        (0, 0, SubjectDir.RIGHT_0),
        N_R,
        ExpectedAngle.FRONT_OF,
        "Subject points right0, neighbour is right",
    ),
    (
        (0, 0, SubjectDir.RIGHT_0),
        N_B,
        ExpectedAngle.RIGHT_OF,
        "Subject points right0, neighbour is below",
    ),
    (
        (0, 0, SubjectDir.RIGHT_0),
        N_L,
        ExpectedAngle.BEHIND_OF,
        "Subject points right0, neighbour is left",
    ),
    # Subject points down
    (
        (0, 0, SubjectDir.DOWN),
        N_A,
        ExpectedAngle.BEHIND_OF,
        "Subject points down, neighbour is above",
    ),
    (
        (0, 0, SubjectDir.DOWN),
        N_R,
        ExpectedAngle.LEFT_OF,
        "Subject points down, neighbour is right",
    ),
    (
        (0, 0, SubjectDir.DOWN),
        N_B,
        ExpectedAngle.FRONT_OF,
        "Subject points down, neighbour is below",
    ),
    (
        (0, 0, SubjectDir.DOWN),
        N_L,
        ExpectedAngle.RIGHT_OF,
        "Subject points down, neighbour is left",
    ),
    # Subject points left
    (
        (0, 0, SubjectDir.LEFT),
        N_A,
        ExpectedAngle.RIGHT_OF,
        "Subject points left, neighbour is above",
    ),
    (
        (0, 0, SubjectDir.LEFT),
        N_R,
        ExpectedAngle.BEHIND_OF,
        "Subject points left, neighbour is right",
    ),
    (
        (0, 0, SubjectDir.LEFT),
        N_B,
        ExpectedAngle.LEFT_OF,
        "Subject points left, neighbour is below",
    ),
    (
        (0, 0, SubjectDir.LEFT),
        N_L,
        ExpectedAngle.FRONT_OF,
        "Subject points left, neighbour is left",
    ),
    # Subject points southwest
    (
        (0, 0, 3.92),
        (-1, 1),
        ExpectedAngle.RIGHT_OF,
        "Subject points southwest, neighbour is northwest",
    ),
    (
        (0, 0, 3.92),
        (1, 1),
        ExpectedAngle.BEHIND_OF,
        "Subject points southwest, neighbour is northeast",
    ),
    (
        (0, 0, 3.92),
        (1, -1),
        ExpectedAngle.LEFT_OF,
        "Subject points southwest, neighbour is southeast",
    ),
    (
        (0, 0, 3.92),
        (-1, -1),
        ExpectedAngle.FRONT_OF,
        "Subject points southwest, neighbour is southwest",
    ),
    # Subject points southeast
    (
        (0, 0, 5.49),
        (-1, 1),
        ExpectedAngle.BEHIND_OF,
        "Subject points southeast, neighbour is northwest",
    ),
    (
        (0, 0, 5.49),
        (1, 1),
        ExpectedAngle.LEFT_OF,
        "Subject points southeast, neighbour is northeast",
    ),
    (
        (0, 0, 5.49),
        (1, -1),
        ExpectedAngle.FRONT_OF,
        "Subject points southeast, neighbour is southeast",
    ),
    (
        (0, 0, 5.49),
        (-1, -1),
        ExpectedAngle.RIGHT_OF,
        "Subject points southeast, neighbour is southwest",
    ),
]


@pytest.mark.parametrize("subject_pose,neighbour_pos,allowe_values,desc", test_data)
def test_calc_neighbour_angle(subject_pose, neighbour_pos, allowe_values, desc):
    # Arrange

    # Act

    actual = calc_relative_angle(
        subject_pos=(subject_pose[0], subject_pose[1]),
        subject_angle=subject_pose[2],
        target_pos=neighbour_pos,
    )

    # Assert
    valid = False
    for expected in allowe_values:
        buffer = 0.2
        if actual < expected + buffer and actual > expected - buffer:
            valid = True
    err_msg = f"Expected {expected}, got {actual}. For {desc}"
    assert valid, err_msg
