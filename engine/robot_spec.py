import math

from engine.types import IRobotSpec
from sim_math.units import Density3d, Distance, Mass, Volume
from sim_math.world_meta import WorldMeta


class Assumptions:
    MOTOR_DENSITY = Density3d.in_kg_m3(5_500)
    BATTERY_DENSITY = Density3d.in_kg_m3(2_500)
    BATTERY_CAPACITY_TO_MASS_RATIO = 150  # Wh/kg
    TORQUE_TO_MOTOR_MASS_RATIO = 3  # Nm/kg


class RobotSpec(IRobotSpec):
    def __init__(self, meta: WorldMeta, battery_mass: Mass, motor_mass: Mass):
        self._meta = meta

        ### Robot dimensions
        motor_volume = self._calc_volume(
            mass=motor_mass, density3d=Assumptions.MOTOR_DENSITY
        )
        battery_volume = self._calc_volume(
            mass=battery_mass, density3d=Assumptions.BATTERY_DENSITY
        )
        volume = battery_volume + motor_volume

        """
        Given the volume (V) the diameter-height ratio (y) let x be:
            x = cuberoot(V / y² * π)
        Then height (h) and diameter (Ø) can be calculated as:
            h = x
            Ø = x * y
        """
        y = 3  # diameter-height ratio
        x = Distance.in_base_unit(
            self._cube_root(volume.base_unit / pow(y, 2) * math.pi)
        )
        height = x
        diameter = x * y
        wheel_radius = height * 0.8 / 2

        ### Physics
        density = self._calc_density3d(mass=battery_mass + motor_mass, volume=volume)
        density2d = density.to_2d(height=height)

        ### Robot performance
        capacity = battery_mass.kg * Assumptions.BATTERY_CAPACITY_TO_MASS_RATIO
        mass_per_motor = motor_mass / 2
        max_motor_torque = mass_per_motor.kg * Assumptions.TORQUE_TO_MOTOR_MASS_RATIO

        super().__init__(
            # Robot dimensions
            robot_diameter=diameter,
            robot_height=height,
            wheel_radius=wheel_radius,
            # Physics
            robot_density_2d=density2d,
            # Robot performance
            battery_capacity__wh=capacity,
            max_motor_torque=max_motor_torque,
        )

    def _cube_root(self, value: float) -> float:
        return value ** (1 / 3)

    def _calc_volume(self, mass: Mass, density3d: Density3d) -> Volume:
        """
        Calculate volume from mass and density3d:
            V = m / D
        where:
            V = volume (m³)
            m = mass (kg)
            D = density (kg/m³)
        """
        return Volume.in_base_unit(mass.kg / density3d.in_kg_m3)

    def _calc_density3d(self, mass: Mass, volume: Volume) -> Density3d:
        """
        Calculate density3d from mass and volume:
            D = m / V
        where:
            D = density3d (kg/m³)
            m = mass (kg)
            V = volume (m³)
        """
        return Density3d.in_kg_m3(mass.kg / volume.m3)
