import math
import pygame
from engine.objects import Box
from engine.helpers import pymunk_to_pygame_point

# Used for calculating the size of the robot
BATTERY_SCALER = 1
MOTOR_SCALER = 1
SIZE_SCALER = 1
# Used to calculate the weight of the robot
BATTERY_DENSITY = 1
MOTOR_DENSITY = 1
WEIGHT_SCALER = 1
# Used to calculate the force of the motors and their power consumption
MOTOR_FORCE_SCALER = 100
MOTOR_POWER_SCALER = 0.001


class RobotBase(Box):
    def __init__(
        self,
        battery_capacity: float,
        motor_strength: float,
        position: tuple = None,
        angle: float = 0,
        color: tuple = None,
    ):
        self.battery_capacity = battery_capacity
        self.battery_left = battery_capacity
        self.motor_strength = motor_strength
        self.up_color = color or (255, 0, 0)
        die_color_scaler = 0.3
        self.down_color = (
            max(min(int(self.up_color[0] * die_color_scaler), 255), 0),
            max(min(int(self.up_color[1] * die_color_scaler), 255), 0),
            max(min(int(self.up_color[2] * die_color_scaler), 255), 0),
        )

        self.size = self._calc_robot_size()
        self.width = math.sqrt(self.size)
        self.weight = self._calc_robot_weight()

        # Call the box constructor
        super().__init__(
            *(position or (0, 0)),
            angle=angle,
            width=self.width,
            length=self.width,
            color=self.up_color,
            density=self._calc_robot_density(),
        )

        self._left_motor = 0
        self._right_motor = 0
        self._force_left = 0
        self._force_right = 0

        # Purely for visualization
        self._wheel_size = 4
        self._wheel_pos_left = (self.left[0] + self._wheel_size, self.left[1])
        self._wheel_pos_right = (self.right[0] - self._wheel_size, self.right[1])

    def set_motor_values(self, left: float, right: float):
        # Clamp the values to -1, 1
        left = max(-1, min(1, left))
        right = max(-1, min(1, right))

        self._left_motor = left
        self._right_motor = right

    def draw(self, surface):
        super().draw(surface)

        # Draw wheels
        left = self.body.local_to_world(self._wheel_pos_left)
        right = self.body.local_to_world(self._wheel_pos_right)
        pygame.draw.circle(
            surface, (0, 0, 0), pymunk_to_pygame_point(left, surface), self._wheel_size
        )
        pygame.draw.circle(
            surface, (0, 0, 0), pymunk_to_pygame_point(right, surface), self._wheel_size
        )

        # Draw direction
        up_left = self.body.local_to_world((self.top[0] - 1, self.top[1]))
        up_right = self.body.local_to_world((self.top[0] + 1, self.top[1]))
        center_left = self.body.local_to_world((-1, 0))
        center_right = self.body.local_to_world((1, 0))
        pygame.draw.polygon(
            surface,
            (0, 0, 0),
            [
                pymunk_to_pygame_point(up_left, surface),
                pymunk_to_pygame_point(center_left, surface),
                pymunk_to_pygame_point(center_right, surface),
                pymunk_to_pygame_point(up_right, surface),
            ],
        )

    def update(self):
        self.controller_update()

        self._force_left = self._calc_motor_force(self._left_motor)
        self._force_right = self._calc_motor_force(self._right_motor)

        self.battery_left -= self._calc_power_consumption()

        if self.battery_left <= 0:
            self.battery_left = 0
            self._force_left = 0
            self._force_right = 0
            self.color = self.down_color

        self.body.apply_force_at_local_point((0, self._force_left), self.left)
        self.body.apply_force_at_local_point((0, self._force_right), self.right)

    def controller_update(self):
        pass

    def _calc_robot_size(self):
        return (
            self.battery_capacity * BATTERY_SCALER + self.motor_strength * MOTOR_SCALER
        ) * SIZE_SCALER

    def _calc_robot_weight(self):
        return (
            self.battery_capacity * BATTERY_DENSITY
            + self.motor_strength * MOTOR_DENSITY
        ) * WEIGHT_SCALER

    def _calc_motor_force(self, motor_value: float):
        return motor_value * self.motor_strength * MOTOR_FORCE_SCALER

    def _calc_power_consumption(self):
        return (
            (abs(self._left_motor) + abs(self._right_motor))
            * self.motor_strength
            * MOTOR_POWER_SCALER
        )

    def _calc_robot_density(self):
        return self.weight / self.size
