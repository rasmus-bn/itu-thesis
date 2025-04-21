from typing import override

from pymunk import Vec2d
from engine.motor import DcMotor
from engine.types import IBattery
from sim_math.units import AngularSpeed, Distance, Torque
from sim_math.world_meta import WorldMeta


class BodyMock:
    def __init__(self):
        self.local_to_world_return_value = (0, 0)
        self.angle = 0

    def local_to_world(self, wheel_position):
        return self.local_to_world_return_value

    def apply_force_at_local_point(force: float = 0, point=None):
        pass


class MetaMock(WorldMeta):
    def __init__(self):
        super().__init__(fps=60)


class BatteryMock(IBattery):
    def __init__(self, meta, body):
        super().__init__(meta=meta, body=body, capacity__wh=0, remaining__wh=100, infinite_power=False, draw_debugging=False, power_draw_scaler=1.0)
        self.get_volts_return_value = None
        self.draw_power_return_value = None

    @override
    def get_volts(self, volts):
        return self.get_volts_return_value if self.get_volts_return_value is not None else volts

    @override
    def draw_power(self, volts, amps):
        return self.draw_power_return_value if self.draw_power_return_value is not None else volts * amps


def get_mocks(max_torque=1, max_voltage=1):
    meta = MetaMock()
    body = BodyMock()
    battery = BatteryMock(meta=meta, body=body)
    motor = DcMotor(
        meta=meta,
        battery=battery,
        body=body,
        max_torque=Torque.in_base_unit(max_torque),
        # max_voltage=max_voltage,
        wheel_position=Vec2d(x=0, y=0),
        wheel_radius=Distance.in_m(1),
    )
    return meta, body, battery, motor


def test_calculate_wheel_speed__moved_forward():
    _, body, _, motor = get_mocks(max_torque=0.1, max_voltage=12)

    # Set the wheel radius
    motor.wheel_radius = Distance.in_base_unit(1)
    # Set the initial wheel position
    motor._wheel_prev_pos = Vec2d(x=0, y=0)
    # Specify gear ratio
    motor._gear_ratio = 2
    # Set the new wheel position
    body.local_to_world_return_value = Vec2d(x=1, y=0)

    motor._calc_motor_speed()

    expected_wheel_speed = 60 * 2
    actual_wheel_speed = motor._wheel_speed.rad_s

    assert actual_wheel_speed == expected_wheel_speed, f"Expected {expected_wheel_speed}, but got {actual_wheel_speed}"


def test_back_emf():
    meta, body, battery, motor = get_mocks(max_torque=0.1, max_voltage=12)

    motor.ke = 0.05  # V/(rad/s)
    motor._wheel_speed = AngularSpeed.in_rad_s(300)  # rad/s

    # Calculate back EMF
    motor._calc_back_emf()

    expected_back_emf = 15  # V
    actual_back_emf = motor._back_emf__v

    assert actual_back_emf == expected_back_emf, f"Expected {expected_back_emf}, but got {actual_back_emf}"


def test_calc_required_amps():
    meta, body, battery, motor = get_mocks(max_torque=0.1, max_voltage=12)

    # Set the back EMF
    torque = Torque.in_nm(2)  # N*m
    motor.kt = 0.1  # Nm/A

    expected_current = 20  # A
    actual_current = motor._calc_required_amps(torque)

    assert actual_current == expected_current, f"Expected {expected_current}, but got {actual_current}"
