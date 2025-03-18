import pytest
from sim_math.world_meta import WorldMeta


test_calc_neighbour_angle_data = [
    (0, 0),
    (37, 79.92),
    (-37, 79.92),
    (1, 2.16),
    (12_345, 26_665.2),
]


@pytest.mark.parametrize("cm_frame,expected_hm_hour", test_calc_neighbour_angle_data)
def test_calc_neighbour_angle(cm_frame, expected_hm_hour):
    # Arrange
    converter = WorldMeta(fps=60)
    buffer = 0.1

    # Act

    actual = converter.convert_speed(cm_frame)

    # Assert
    valid = False
    if actual < expected_hm_hour + buffer and actual > expected_hm_hour - buffer:
        valid = True
    err_msg = (
        f"Expected {cm_frame} cm/frames == {expected_hm_hour} km/h, got {actual} km/h."
    )
    assert valid, err_msg
