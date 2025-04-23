from collections.abc import Callable
from typing import override
import pygame
from pymunk import Body, Vec2d
from engine.types import IBattery, IMotor
from sim_math.units import AngularSpeed, Distance, Force, TimeSpan, Torque


class DcMotorAssumptions:
    KT = 0.2  # Torque constant - Nm/A (kT)
    KE = 42  # Back EMF constant - V/krpm (kE)
    RESISTANCE = 0.1  # Resistance - Ohm (R)


class DcMotor(IMotor):
    def __init__(
        self,
        meta,
        battery: IBattery,
        body: Body,
        max_torque: Torque,
        # max_voltage: float,
        wheel_position: tuple[float, float],
        wheel_radius: Distance,
        unrestricted_force: bool = False,
        draw_debugging: bool = False,
        print_math: bool = False,
        motor_force_scaler: float = 1.0,
    ):
        super().__init__(
            meta=meta,
            battery=battery,
            body=body,
            wheel_position=wheel_position,
            wheel_radius=wheel_radius,
            unrestricted_force=unrestricted_force,
            draw_debugging=draw_debugging,
            print_math=print_math,
            motor_force_scaler=motor_force_scaler,
        )
        self._gear_ratio = 9

        self.max_force = self._to_robot_force(motor_torque=max_torque)
        # self.max_voltage = max_voltage
        self._wheel_prev_pos = self.body.local_to_world(self.wheel_position)
        self._wheel_speed = AngularSpeed.in_base_unit(0.0)
        self._back_emf__v = 0.0
        self._force = Force.in_base_unit(0.0)
        self._explanation_points = []

        self.ke = DcMotorAssumptions.KE / AngularSpeed.in_krpm(1).rad_s  # Convert to V/(rad/s)
        self.kt = DcMotorAssumptions.KT  # Torque constant - Nm/A
        self.resistance = DcMotorAssumptions.RESISTANCE  # Resistance - Ohm (R)

        # Purely for visualization
        self._wheel_size = self.wheel_radius.base_unit
        self._wheel_pos_left = (
            self.wheel_position[0] * 0.9,
            self.wheel_position[1] * 0.9,
        )

    @override
    def request_force(self, force: Force) -> None:
        """Requests a force (N) to be applied to the wheel.
        The force is applied at the wheel position during the postupdate phase.
        """
        if not self.unrestricted_force:
            force = max(-self.max_force, min(self.max_force, force))
        self._force = force

    @override
    def request_force_scaled(self, force_scaler: float) -> None:
        """Requests a to be applied to the wheel from a value of -1 to 1.
        The force is applied at the wheel position during the postupdate phase.
        """
        self.request_force(force=self.max_force * force_scaler)

    @override
    def preupdate(self):
        self._explain(lambda: f"1 timestep = 1/{TimeSpan.in_second(1).base_unit:.0f}s")
        self._explain(lambda: f"Max force: {self.max_force.n:.2f}N")
        self._explain(lambda: f"Gear ratio: {self._gear_ratio}:1")
        self._calc_motor_speed()
        self._calc_back_emf()

    @override
    def update(self):
        self._apply_force()

    @override
    def postupdate(self):
        if self.print_math:
            print("----------------------------------------------")
            print("DC motor reasoning:")
            for i, point in enumerate(self._explanation_points):
                print(f"  - [{(i + 1):02d}] {point}")
            self._explanation_points.clear()
            print("----------------------------------------------")

    @override
    def draw(self, surface):
        # Draw wheels as dots
        global_pos = self.body.local_to_world(self._wheel_pos_left)
        pygame.draw.circle(
            surface=surface,
            color=(0, 0, 0),
            center=self.meta.pymunk_to_pygame_point(global_pos, surface),
            radius=self.meta.pymunk_to_pygame_scale(self._wheel_size),
        )

    def _explain(self, func: Callable[[], str]):
        """Prints the reasoning for the force applied to the wheel."""
        if self.print_math:
            self._explanation_points.append(func())

    def _apply_force(self):
        """Applies the force to the wheel based on the requested force.
        The force is applied at the wheel position.
        """
        requested_torque = self._to_motor_torque(force=self._force)
        self._explain(lambda: f"Requested force: {self._force.n:.2f}N at wheel radius {self.wheel_radius.m:.2f}m -> torque: {requested_torque.nm:.2f}Nm")
        amps = self._calc_required_amps(t=requested_torque)
        volts = self._calc_volts_to_achieve_amps(amps=amps)
        # self._explain(lambda: f"Capping voltage {volts:.2f}V to max voltage {self.max_voltage:.2f}V")
        # volts = min(volts, self.max_voltage)
        got_power = self.battery.draw_power(volts=volts, amps=amps)

        if got_power:
            # Forward force
            force = self._force.base_unit * self.motor_force_scaler
            force_vector = (force, 0)
            self._explain(lambda: f"Applying force: {self._force.n:.2f}N, meaning torque: {requested_torque.nm:.2f}Nm")
            self.body.apply_force_at_local_point(force=force_vector, point=self.wheel_position)

    def _calc_motor_speed(self):
        """Calculates the wheel speed in rad/s based on the distance traveled by the wheel."""
        current_pos = self.body.local_to_world(self.wheel_position)
        dist_vector = current_pos - self._wheel_prev_pos
        self._explain(lambda: f"Distance vector: ({dist_vector.x:.1f}, {dist_vector.y:.1f}) (cm) from ({self._wheel_prev_pos.x:.1f}, {self._wheel_prev_pos.y:.1f}) to ({current_pos.x:.1f}, {current_pos.y:.1f})")
        self._wheel_prev_pos = current_pos

        direction_vector = Vec2d(1, 0).rotated(self.body.angle)
        self._explain(lambda: f"Direction vector: ({direction_vector.x:.1f}, {direction_vector.y:.1f}) (cm), given angle: {self.body.angle:.1f}rad (right is 0rad)")
        # The distance traveled in the direction of the wheel
        dist_in_direction = dist_vector.dot(direction_vector)
        self._explain(lambda: f"Distance in the direction: {dist_in_direction:.1f} (cm)")

        # Calculates the wheel speed in rad/timestep
        if dist_in_direction == 0:
            self._wheel_speed = AngularSpeed.in_base_unit(0.0)
        else:
            self._wheel_speed = AngularSpeed.in_base_unit((self._gear_ratio * dist_in_direction) / self.wheel_radius.base_unit)
        self._explain(lambda: f"With wheel radius of {self.wheel_radius.to_str(Distance.CM, 1)} and gear raio {self._gear_ratio}:1, motor speed: {self._wheel_speed.to_str(AngularSpeed.RAD_S, 1)} or {self._wheel_speed.to_str(AngularSpeed.RPM, 1)}")

    def _calc_back_emf(self):
        """Calculates the back EMF based on the wheel speed.
        The back EMF is the voltage (V) generated by the motor when it is spinning.
            E = kE * ω
        where:
            E = back EMF (V)
            kE = back EMF constant (V/(rad/s))
            ω = wheel speed (rad/s)
        """
        self._back_emf__v = self.ke * self._wheel_speed.rad_s
        self._explain(lambda: f"Given the motors kE {self.ke:.2f}V/(rad/s) and the wheel speed {self._wheel_speed.to_str(AngularSpeed.RAD_S, 2)} or {self._wheel_speed.to_str(AngularSpeed.RPM, 2)} the back EMF is {self._back_emf__v:.2f}V.")

    def _calc_required_amps(self, t: Torque) -> float:
        """Calculates the required amps to achieve the desired torque.
        The amps are calculated using the torque constant (kT).
            T = kT * I   == solve I ==>   I = T / kT
        where:
            I = current (A)
            T = torque (Nm)
            kT = torque constant (Nm/A)
        """
        if t.base_unit == 0:
            self._explain(lambda: "Torque is zero, no amps required.")
            return 0.0
        amps = t.nm / self.kt
        self._explain(lambda: f"To achieve torque: {t.nm:.2f}Nm with the motor's torque constant {self.kt:.2f}Nm/A requires {amps:.2f}A")
        return amps

    def _calc_volts_to_achieve_amps(self, amps: float) -> float:
        """Calculates the required volts to achieve the desired amps.
        The volts are calculated using the resistance and back EMF.
            I = (V - E) / R   == solve V ==>   V = I * R + E
        where:
            V = voltage (V)
            I = current (A)
            R = resistance (Ohm)
            E = back EMF (V)
        """
        volts = amps * self.resistance + self._back_emf__v
        self._explain(lambda: f"To achieve {amps:.2f}A with the motor's resistance {self.resistance:.2f}Ohm and back EMF {self._back_emf__v:.2f}V requires {volts:.2f}V")
        return volts

    def _to_robot_force(self, motor_torque: Torque) -> Force:
        """Converts the motor torque to a force at the wheel position.
        The force is calculated using the formula:
            F = (G * T) / r
        where:
            F = force (N)
            G = gear ratio (dimensionless)
            T = torque (Nm)
            r = wheel radius (m)
        """
        if motor_torque.base_unit == 0:
            return Force.in_n(0.0)
        force = (self._gear_ratio * motor_torque.nm) / self.wheel_radius.m
        return Force.in_n(force)

    def _to_motor_torque(self, force: Force) -> Torque:
        """Converts the force at the wheel position to a motor torque.
        The torque is calculated using the formula:
            T = (F * r) / G
        where:
            T = torque (Nm)
            F = force (N)
            r = wheel radius (m)
            G = gear ratio (dimensionless)
        """
        if force.base_unit == 0:
            return Torque.in_nm(0.0)
        torque = (force.n * self.wheel_radius.m) / self._gear_ratio
        return Torque.in_nm(torque)
