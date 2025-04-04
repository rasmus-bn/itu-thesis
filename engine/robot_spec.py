class Assumptions:
    MOTOR_DENSITY = 0.5  # kg/m³
    BATTERY_DENSITY = 0.5  # kg/m³
    BATTERY_CAPACITY_TO_MASS_RATIO = 1000  # Wh/kg
    TORQUE_TO_MOTOR_MASS_RATIO = 0.1  # Nm/kg


class RobotSpec:
    def __init__(self, battery_mass_kg: float = 0.1, motor_mass_kg: float = 0.1):
        self.battery_mass_kg = battery_mass_kg
        self.motor_mass_kg = motor_mass_kg

        # Differential drive robot
        self.motor_count = 2

        # Robot volume
        self.motor_volume_m3 = self.motor_mass_kg / Assumptions.MOTOR_DENSITY
        self.battery_volume_m3 = self.battery_mass_kg / Assumptions.BATTERY_DENSITY
        self.total_volume_m3 = self.battery_volume_m3 + self.motor_volume_m3

        # Robot dimensions
        # TODO

        # Battery capacity
        self.battery_capacity_wh = (
            self.battery_mass_kg * Assumptions.BATTERY_CAPACITY_TO_MASS_RATIO
        )

        # Motor torque
        self.robot_torque_nm = (
            self.motor_mass_kg * Assumptions.TORQUE_TO_MOTOR_MASS_RATIO
        )
        self.motor_torque_nm = self.robot_torque_nm / self.motor_count
