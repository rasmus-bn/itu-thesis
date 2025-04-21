import math

from pymunk import Space
from engine.objects import Circle
from engine.robot_spec import RobotSpec, Assumptions
from sim_math.units import Mass


def test_volume_correct():
    spec = RobotSpec(meta=None, battery_mass=Mass.in_kg(30), motor_mass=Mass.in_kg(100))

    # Calculated expected volume of the cylindrical robot based on diameter and height
    expected_volume = (spec.robot_diameter.m / 2) ** 2 * spec.robot_height.m * math.pi
    actual_volume = spec.robot_volume.m3

    assert math.isclose(
        expected_volume,
        actual_volume,
        rel_tol=1e-9,
    ), f"Expected volume: {expected_volume}m3, but got: {actual_volume}m3"


def test_density_correct():
    spec = RobotSpec(meta=None, battery_mass=Mass.in_kg(30), motor_mass=Mass.in_kg(100))

    # Calculated expected density based on mass and volume
    expected_density = spec.total_mass.kg / spec.robot_volume.m3
    actual_density = spec.robot_density_3d.kg_m3

    assert math.isclose(
        expected_density,
        actual_density,
        rel_tol=1e-9,
    ), f"Expected density: {expected_density}kg/m2, but got: {actual_density}kg/m3"


def test_mass_percentage():
    spec = RobotSpec(meta=None, battery_mass=Mass.in_kg(1), motor_mass=Mass.in_kg(1))

    # Calculate the expected mass percentages
    total_mass = spec.total_mass.kg
    other_materials_mass_percentage = ((total_mass - spec.battery_mass.kg - spec.motor_mass.kg) / total_mass) * 100

    assert math.isclose(
        other_materials_mass_percentage,
        Assumptions.OTHER_MATERIALS_PERCENTAGE,
        rel_tol=1e-9,
    ), f"Expected other materials mass percentage: {Assumptions.OTHER_MATERIALS_PERCENTAGE}%, but got: {other_materials_mass_percentage}%"


def test_pymunk_body_mass():
    spec = RobotSpec(meta=None, battery_mass=Mass.in_kg(1), motor_mass=Mass.in_kg(1))
    circle = Circle(x=0, y=0, radius=spec.robot_diameter.m / 2, density=spec.robot_density_2d.kg_m2, sim=None)

    space = Space()
    space.add(circle.body, circle.shape)
    space.step(0.1)
    expected = spec.total_mass.kg
    actual = circle.body.mass

    assert math.isclose(
        expected,
        actual,
        rel_tol=1e-9,
    ), f"Expected pymunk body mass: {expected}kg, but got: {actual}kg"
