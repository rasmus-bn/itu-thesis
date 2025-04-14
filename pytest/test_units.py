import pytest
from sim_math.units import (
    Distance,
    TimeSpan,
    Volume,
    Mass,
    Density2d,
    Density3d,
    Force,
    Torque,
    Speed,
    AngularSpeed,
)

TimeSpan.initialize(fps=60)
Speed.initialize(fps=60)
AngularSpeed.initialize(fps=60)


@pytest.mark.parametrize(
    "first, second",
    [
        (Distance.in_cm(1), Distance.in_m(0.01)),
        (Distance.in_m(1), Distance.in_km(0.001)),
        (Distance.in_km(1), Distance.in_m(1000)),
        (Distance.in_cm(1), Distance.in_km(0.00001)),
        (Distance.in_m(1), Distance.in_cm(100)),
        (Distance.in_km(1), Distance.in_cm(100000)),
        (Distance.in_cm(100), Distance.in_m(1)),
        (Distance.in_m(100), Distance.in_km(0.1)),
    ],
)
def test_distance(first, second):
    # Assert
    is_almost_equal = abs(first - second) < 1e-6
    assert is_almost_equal, f"Expected {first} to be {second}"


@pytest.mark.parametrize(
    "first, second",
    [
        (TimeSpan.in_second(1), TimeSpan.in_minute(0.0166666666666667)),
        (TimeSpan.in_minute(1), TimeSpan.in_hour(0.0166666666666667)),
        (TimeSpan.in_hour(1), TimeSpan.in_second(3600)),
        (TimeSpan.in_second(1), TimeSpan.in_hour(0.000277777777777778)),
        (TimeSpan.in_minute(1), TimeSpan.in_second(60)),
    ],
)
def test_time(first, second):
    # Assert
    is_almost_equal = abs(first - second) < 1e-6
    assert is_almost_equal, f"Expected {first} to be {second}"


@pytest.mark.parametrize(
    "first, second",
    [
        (Volume.in_cm3(1), Volume.in_litre(0.001)),
        (Volume.in_litre(1), Volume.in_m3(0.001)),
        (Volume.in_m3(1), Volume.in_cm3(1000000)),
        (Volume.in_cm3(1000), Volume.in_litre(1)),
        (Volume.in_litre(1), Volume.in_cm3(1000)),
    ],
)
def test_volume(first, second):
    # Assert
    is_almost_equal = abs(first - second) < 1e-6
    assert is_almost_equal, f"Expected {first} to be {second}"


@pytest.mark.parametrize(
    "first, second",
    [
        (Mass.in_g(1), Mass.in_kg(0.001)),
        (Mass.in_kg(1), Mass.in_g(1000)),
    ],
)
def test_mass(first, second):
    # Assert
    is_almost_equal = abs(first - second) < 1e-6
    assert is_almost_equal, f"Expected {first} to be {second}"


@pytest.mark.parametrize(
    "first, second",
    [
        (Density2d.in_g_cm2(1), Density2d.in_kg_m2(10)),
        (Density2d.in_kg_m2(1), Density2d.in_g_cm2(0.1)),
        (Density2d.in_g_cm2(10), Density2d.in_kg_m2(100)),
        (Density2d.in_kg_m2(4), Density2d.in_g_cm2(0.4)),
    ],
)
def test_density_2d(first, second):
    # Assert
    is_almost_equal = abs(first - second) < 1e-6
    assert is_almost_equal, f"Expected {first} to be {second}"


@pytest.mark.parametrize(
    "first, second",
    [
        (Density3d.in_g_cm3(1), Density3d.in_kg_m3(1000)),
        (Density3d.in_kg_m3(1), Density3d.in_g_cm3(0.001)),
        (Density3d.in_g_cm3(10), Density3d.in_kg_m3(10000)),
        (Density3d.in_kg_m3(4), Density3d.in_g_cm3(0.004)),
    ],
)
def test_density_3d(first, second):
    # Assert
    is_almost_equal = abs(first - second) < 1e-6
    assert is_almost_equal, f"Expected {first} to be {second}"


@pytest.mark.parametrize(
    "dens_2d, height, dens_3d",
    [
        (Density2d.in_g_cm2(1), Distance.in_cm(1), Density3d.in_g_cm3(1)),
        (Density2d.in_kg_m2(1), Distance.in_cm(1), Density3d.in_g_cm3(0.1)),
        (Density2d.in_kg_m2(1), Distance.in_m(1), Density3d.in_g_cm3(0.001)),
        (Density2d.in_g_cm2(10), Distance.in_cm(10), Density3d.in_g_cm3(1)),
        (Density2d.in_kg_m2(4), Distance.in_m(4), Density3d.in_kg_m3(1)),
    ],
)
def test_density_2d_to_3d(dens_2d, height, dens_3d):
    # Act
    converted = dens_2d.to_3d(height)

    # Assert
    is_almost_equal = abs(converted - dens_3d) < 1e-6
    assert is_almost_equal, f"Expected {converted} to be {dens_3d}"


@pytest.mark.parametrize(
    "first, second",
    [
        (Force.in_n(1), Force.in_dyne(100000)),
        (Force.in_dyne(1), Force.in_n(0.00001)),
    ],
)
def test_force(first, second):
    # Assert
    is_almost_equal = abs(first - second) < 1e-6
    assert is_almost_equal, f"Expected {first} to be {second}"


@pytest.mark.parametrize(
    "force, radius, torque",
    [
        (Force.in_n(1), Distance.in_m(1), Torque.in_nm(1)),
        (Force.in_dyne(1), Distance.in_cm(1), Torque.in_dyne_cm(1)),
        (Force.in_n(1), Distance.in_m(1), Torque.in_nm(1)),
        (Force.in_n(1), Distance.in_cm(100), Torque.in_dyne_cm(10_000_000)),
    ],
)
def test_force_to_torque(force, radius, torque):
    # Act
    converted = force.to_torque_at(radius)

    # Assert
    is_almost_equal = abs(converted - torque) < 1e-6
    assert is_almost_equal, f"Expected {converted} to be {torque}"


@pytest.mark.parametrize(
    "first, second",
    [
        (Torque.in_nm(1), Torque.in_dyne_cm(10_000_000)),
        (Torque.in_dyne_cm(1), Torque.in_nm(0.000_000_1)),
    ],
)
def test_torque(first, second):
    # Assert
    is_almost_equal = abs(first - second) < 1e-6
    assert is_almost_equal, f"Expected {first} to be {second}"


@pytest.mark.parametrize(
    "torque, radius, force",
    [
        (Torque.in_nm(1), Distance.in_m(1), Force.in_n(1)),
        (Torque.in_dyne_cm(1), Distance.in_cm(1), Force.in_dyne(1)),
        (Torque.in_nm(1), Distance.in_m(1), Force.in_n(1)),
        (Torque.in_dyne_cm(10_000_000), Distance.in_cm(100), Force.in_n(1)),
    ],
)
def test_torque_to_force(torque, radius, force):
    # Act
    converted = torque.to_force_at(radius)

    # Assert
    is_almost_equal = abs(converted - force) < 1e-6
    assert is_almost_equal, f"Expected {converted} to be {force}"


@pytest.mark.parametrize(
    "first, second",
    [
        (Speed.in_cm_s(1), Speed.in_km_h(0.036)),
        (Speed.in_km_h(1), Speed.in_cm_s(27.7777777777778)),
        (Speed.in_km_h(1), Speed.in_base_unit(0.462962963)),
        (Speed.in_base_unit(100), Speed.in_km_h(216)),
        (Speed.in_km_h(3.6), Speed.in_base_unit(1.6666666666)),
        (Speed.in_base_unit(1), Speed.in_cm_s(60)),
    ],
)
def test_speed(first, second):
    # Assert
    is_almost_equal = abs(first - second) < 1e-6
    assert is_almost_equal, f"Expected {first} to be {second}"


@pytest.mark.parametrize(
    "first, second",
    [
        (AngularSpeed.in_rad_s(60), AngularSpeed.in_base_unit(1)),
        (AngularSpeed.in_rpm(1), AngularSpeed.in_rad_s(0.10471975511965977)),
        (AngularSpeed.in_rad_s(1), AngularSpeed.in_rpm(9.549296585513721)),
    ],
)
def test_angular_speed(first, second):
    # Assert
    is_almost_equal = abs(first - second) < 1e-6
    assert is_almost_equal, f"Expected {first} to be {second}"
