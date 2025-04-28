import math

from engine.types import IRobotSpec
from sim_math.units import Density2d, Density3d, Distance, Mass, Torque, Volume
from sim_math.world_meta import WorldMeta


class Assumptions:
    # For reference water is 1000 kg/m³
    MOTOR_DENSITY = Density3d.in_kg_m3(5_500)
    BATTERY_DENSITY = Density3d.in_kg_m3(2_500)
    OTHER_MATERIALS_DENSITY = Density3d.in_kg_m3(1000)

    BATTERY_CAPACITY_TO_MASS_RATIO = 150  # Wh/kg
    TORQUE_TO_MOTOR_MASS_RATIO = 8  # Nm/kg
    VOLTAGE_TO_MOTOR_MASS_RATIO = 10  # V/kg


class RobotSpec(IRobotSpec):
    def __init__(self, meta: WorldMeta, battery_mass: Mass, motor_mass: Mass, other_materials_mass: Mass):
        self._meta = meta

        ### Robot dimensions
        motor_volume = self._calc_volume(mass=motor_mass, density3d=Assumptions.MOTOR_DENSITY)
        battery_volume = self._calc_volume(mass=battery_mass, density3d=Assumptions.BATTERY_DENSITY)
        total_mass = battery_mass + motor_mass + other_materials_mass

        # print(battery_mass.kg, motor_mass.kg, other_materials_mass.kg)

        other_materials_volume = self._calc_volume(mass=other_materials_mass, density3d=Assumptions.OTHER_MATERIALS_DENSITY)
        volume = battery_volume + motor_volume + other_materials_volume

        """
        Given the volume (V) the diameter-height ratio (y) let x be:
            x = cuberoot(V / (y² * π))
        Then height (h) and diameter (Ø) can be calculated as:
            h = x
            Ø = x * y
        """
        y = 3  # diameter-height ratio
        x = Distance.in_base_unit(self._cube_root(4 * volume.base_unit / (pow(y, 2) * math.pi)))
        height = x
        diameter = x * y
        wheel_radius = height * 0.8 / 2

        ### Physics
        density3d = self._calc_density3d(mass=total_mass, volume=volume)
        density2d = density3d.to_2d(height=height)

        ### Robot performance
        capacity = battery_mass.kg * Assumptions.BATTERY_CAPACITY_TO_MASS_RATIO
        mass_per_motor = motor_mass / 2
        max_motor_torque = Torque.in_nm(mass_per_motor.kg * Assumptions.TORQUE_TO_MOTOR_MASS_RATIO)
        # max_motor_voltage = mass_per_motor.kg * Assumptions.VOLTAGE_TO_MOTOR_MASS_RATIO

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
            # max_motor_voltage=max_motor_voltage,
            # Meta data
            robot_volume=volume,
            battery_mass=battery_mass,
            motor_mass=motor_mass,
            other_mass=other_materials_mass,
            total_mass=total_mass,
            robot_density_3d=density3d,
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
        return Volume.in_m3(mass.kg / density3d.kg_m3)

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

    def get_spec_sheet(self) -> str:
        def r(value: float, decimals: int) -> float:
            return round(value, decimals)

        return (
            f"----------------------------------------------\n"
            f"Robot Diameter: {self.robot_diameter.to_str(Distance.M, 2)}\n"
            f"Robot Height: {self.robot_height.to_str(Distance.M, 2)}\n"
            f"Wheel Radius: {self.wheel_radius.to_str(Distance.M, 2)}\n"
            f"Robot Density 2D (engine): {self.robot_density_2d.to_str(Density2d.KG_M2, 2)}\n"
            f"Robot Density 3D (real world): {self.robot_density_3d.to_str(Density3d.KG_M3, 3)}\n"
            f"Battery Capacity: {r(self.battery_capacity__wh, 2)} Wh\n"
            f"Max Motor Torque: {self.max_motor_torque.to_str(Torque.NM, 2)}\n"
            # f"Max Motor Voltage: {r(self.max_motor_voltage, 2)} V\n"
            f"Robot Volume: {self.robot_volume.to_str(Volume.M3, 2)} or {self.robot_volume.to_str(Volume.CM3, 2)} \n"
            f"Battery Mass: {self.battery_mass.to_str(Mass.KG, 3)}\n"
            f"Motor Mass: {self.motor_mass.to_str(Mass.KG, 3)}\n"
            f"Other Mass: {self.other_mass.to_str(Mass.KG, 3)}\n"
            f"Total mass: {self.total_mass.to_str(Mass.KG, 3)}\n"
            f"----------------------------------------------\n"
        )
