from dataclasses import dataclass
import pygame

from algorithms.control_api import RobotControlAPI
from algorithms.sensor_api import RobotSensorAPI
from engine.tether import Tether
from engine.gpt_generated.closest_point_on_circle import closest_point_on_circle
from engine.environment import Resource
from engine.objects import Box, IGameObject
from engine.helpers import pymunk_to_pygame_point
from sim_math.angles import calc_relative_angle
import numpy as np
import pymunk

from engine.types import ILidarData, ILightData

# Used for calculating the size of the robot
BATTERY_SCALER = 1
MOTOR_SCALER = 1
SIZE_SCALER = 1
# Used to calculate the weight of the robot
BATTERY_DENSITY = 0.1
MOTOR_DENSITY = 0.1
WEIGHT_SCALER = 1
# Used to calculate the force of the motors and their power consumption
MOTOR_FORCE_SCALER = 100
MOTOR_POWER_SCALER = 0.001


class RobotBase(Box):
    _robot_counter = 1  # Keeps track of unique robot IDs

    def __init__(
        self,
        battery_volume: float,
        motor_volume: float,
        position: tuple = None,
        angle: float = 0,
        color: tuple = None,
        num_ir_sensors: int = 8,
        sensor_range: float = 50.0,
        controller: any = None,
        ignore_battery: bool = False,
    ):
        self._comms_range = 50
        self.message: None | str = None
        self.received_messages: list[str] = []

        self._light_range = 200
        self.light_switch = False
        self.light_detectors: list[ILightData] = []

        self.ignore_battery = ignore_battery
        self.battery_capacity = battery_volume  # TODO: find proper unit and convertion
        self.motor_strength = motor_volume  # TODO: find proper unit and convertion

        self.speedometer = 0

        self.battery_volume = battery_volume
        self.motor_volume = motor_volume

        # Battery remaining in the robot
        self.battery_remaining = self.battery_capacity  # TODO: Verify proper unit
        self.up_color = color or (255, 0, 0)
        die_color_scaler = 0.3
        self.down_color = (
            max(min(int(self.up_color[0] * die_color_scaler), 255), 0),
            max(min(int(self.up_color[1] * die_color_scaler), 255), 0),
            max(min(int(self.up_color[2] * die_color_scaler), 255), 0),
        )

        self.total_volume = self.battery_volume + self.motor_volume
        # Cube root of the volume (for 3D cube)
        self.side_length = self.total_volume ** (1 / 3)

        self.mass = self._calc_robot_mass()

        self.tether: Tether | None = None

        # Call the box constructor
        super().__init__(
            *(position or (0, 0)),
            angle=angle,
            width=self.side_length,
            length=self.side_length,
            color=self.up_color,
            density=self._calc_robot_density(),
            virtual_height=self.side_length,
        )

        self._left_motor = 0
        self._right_motor = 0
        self._force_left = 0
        self._force_right = 0

        # Purely for visualization
        self._wheel_size = 4
        self._wheel_pos_left = (self.top[0], self.top[1] - self._wheel_size)
        self._wheel_pos_right = (self.bottom[0], self.bottom[1] + self._wheel_size)

        # Sensor setup
        self.num_ir_sensors = num_ir_sensors
        self._lidar_range = sensor_range
        self.ir_sensors: list[ILidarData] = self._initialize_ir_sensors()

        # Set up the shape filter (ignores itself but detects other objects)
        self.robot_group = RobotBase._robot_counter
        RobotBase._robot_counter += 1

        self.shape.filter = pymunk.ShapeFilter(
            categories=0b0001,  # This object is a robot
            mask=0b0001 | 0b0010 | 0b0100,  # Detects robots, obstacles, and goals
            group=self.robot_group,  # Ignores itself
        )

        # Create API objects
        sensors = RobotSensorAPI(self)
        controls = RobotControlAPI(self)

        # Assign APIs to the controller
        self.controller = controller
        if controller:
            self.controller.set_apis(sensors, controls)

    def set_motor_values(self, left: float, right: float):
        # Clamp the values to -1, 1
        left = max(-1, min(1, left))
        right = max(-1, min(1, right))

        self._left_motor = left
        self._right_motor = right

    def set_message(self, message: str):
        self.message = message

    def get_received_messages(self) -> list[str]:
        return self.received_messages

    def attach_to_resource(self, resource: Resource):
        if self.tether:
            if self.tether.resource == resource:
                return
            else:
                self.detach_from_resource()

        offset_global = closest_point_on_circle(
            subject_center=self.body.position,
            circle_center=resource.body.position,
            circle_radius=resource.radius,
        )
        offset = resource.body.world_to_local(offset_global)

        self.tether = Tether(robot=self, resource=resource, resource_offset=offset)
        self.sim.add_tether(self.tether)
        print(f"attached: {resource}")

    def detach_from_resource(self):
        if self.tether:
            self.sim.remove_tether(self.tether)
            self.tether = None

    def _initialize_ir_sensors(self):
        sensors: list[ILidarData] = []
        angle_step = 2 * np.pi / self.num_ir_sensors  # Distribute sensors equally

        for i in range(self.num_ir_sensors):
            angle = self.body.angle + (i * angle_step)  # Compute sensor angle
            sensors.append(
                ILidarData(angle=angle, distance=self._lidar_range, gameobject=None)
            )

        return sensors

    def preupdate(self):
        ray_filter = pymunk.ShapeFilter(
            mask=0b0001 | 0b0010 | 0b0100, group=self.robot_group
        )
        # IR sensor (or LIDAR)
        for sensor in self.ir_sensors:
            sensor_pos = self.body.position  # Robot's center
            direction = (
                np.cos(self.body.angle + sensor.angle),
                np.sin(self.body.angle + sensor.angle),
            )

            # Raycast in sensor direction
            # print(f"using group: {self.robot_group}")

            hit = self.sim.space.segment_query_first(
                sensor_pos,  # start of the ray
                (
                    sensor_pos[0] + direction[0] * self._lidar_range,
                    sensor_pos[1] + direction[1] * self._lidar_range,
                ),  # end of the ray
                1.0,  # Radius of ray
                shape_filter=ray_filter,
            )

            if hit:
                sensor.distance = hit.alpha * self._lidar_range
                sensor.gameobject = hit.shape.body.gameobject
            else:
                sensor.distance = self._lidar_range
                sensor.gameobject = None

        # Light emitter
        if self.light_switch:
            query_result = self.body.space.point_query(
                self.body.position, self._light_range, ray_filter
            )
            for result in query_result:
                body: pymunk.Body = result.shape.body
                robot: RobotBase = body.gameobject
                if isinstance(robot, RobotBase):
                    distance = result.distance
                    angle = calc_relative_angle(
                        subject_pos=body.position,
                        subject_angle=body.angle,
                        target_pos=self.body.position,
                    )
                    # Add the emitter to the target's detections
                    robot.light_detectors.append(ILightData(distance, angle))

        # Send message
        if self.message:
            query_result = self.body.space.point_query(
                self.body.position, self._comms_range, ray_filter
            )
            for result in query_result:
                robot: RobotBase = result.shape.body.gameobject
                if isinstance(robot, RobotBase):
                    # print(f"Robot {self} has {robot} in communication range {self._comms_range}")
                    self.received_messages.append(robot.message)

        # # Update speedometer
        # self.speedometer = np.linalg.norm(self.body.velocity)

    def postupdate(self):
        self.light_detectors.clear()
        self.received_messages.clear()

    def draw_sensors(self, screen):
        for sensor in self.ir_sensors:
            sensor_pos = self.body.position  # Robot's center
            direction = (
                np.cos(self.body.angle + sensor.angle),
                np.sin(self.body.angle + sensor.angle),
            )

            # Compute sensor end position
            sensor_end = (
                sensor_pos[0] + direction[0] * sensor.distance,
                sensor_pos[1] + direction[1] * sensor.distance,
            )

            # Choose color: RED if sensor detects an object, GREEN if nothing detected
            color = (255, 0, 0) if sensor.distance < self._lidar_range else (0, 255, 0)

            # Convert Pymunk coordinates to Pygame coordinates
            start_pos = (int(sensor_pos[0]), int(sensor_pos[1]))
            end_pos = (int(sensor_end[0]), int(sensor_end[1]))

            start_pos = pymunk_to_pygame_point(start_pos, screen)
            end_pos = pymunk_to_pygame_point(end_pos, screen)

            # Draw sensor ray
            pygame.draw.line(screen, color, start_pos, end_pos, 2)

            if sensor.gameobject is not None:
                obj = sensor.gameobject
                if isinstance(obj, Resource):
                    pygame.draw.circle(screen, (200, 200, 0), end_pos, 10)
                if isinstance(obj, RobotBase):
                    pygame.draw.circle(screen, (200, 0, 0), end_pos, 10)

        # Draw light sensor
        if self.light_detectors:
            for light in self.light_detectors:
                angle = self.body.angle + light.angle
                direction = (
                    np.cos(angle),
                    np.sin(angle),
                )
                end_pos = (
                    self.body.position[0] + direction[0] * light.distance,
                    self.body.position[1] + direction[1] * light.distance,
                )
                pygame.draw.line(
                    screen,
                    (255, 255, 0),
                    pymunk_to_pygame_point(self.body.position, screen),
                    pymunk_to_pygame_point(end_pos, screen),
                    2,
                )

    def send_your_message(self):
        pass
        # todo: implement local communication

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
        right_up = self.body.local_to_world((self.right[0], self.right[1] + 1))
        right_down = self.body.local_to_world((self.right[0], self.right[1] - 1))
        center_up = self.body.local_to_world((0, +1))
        center_down = self.body.local_to_world((0, -1))
        pygame.draw.polygon(
            surface,
            (0, 255, 0),
            [
                pymunk_to_pygame_point(center_up, surface),
                pymunk_to_pygame_point(center_down, surface),
                pymunk_to_pygame_point(right_down, surface),
                pymunk_to_pygame_point(right_up, surface),
            ],
        )

        # Draw light emitter
        if self.light_switch:
            x, y = pymunk_to_pygame_point(self.body.position, surface=surface)
            pygame.draw.circle(
                surface=surface,
                color=(255, 255, 0),
                center=(x, y),
                radius=self._light_range,
                width=1,
            )

    def update(self):
        # todo change
        self.controller_update()
        if self.controller:
            self.controller.update()

        self._force_left = self._calc_motor_force(self._left_motor)
        self._force_right = self._calc_motor_force(self._right_motor)

        if not self.ignore_battery:
            self.battery_remaining -= self._calc_power_consumption()
            if self.battery_remaining <= 0:
                self.battery_remaining = 0
                self._force_left = 0
                self._force_right = 0
                self.color = self.down_color

        self.body.apply_force_at_local_point((self._force_left, 0), self.top)
        self.body.apply_force_at_local_point((self._force_right, 0), self.bottom)

    def controller_update(self):
        pass

    def _calc_robot_mass(self):
        return self.battery_volume * BATTERY_DENSITY + self.motor_volume * MOTOR_DENSITY

    def _calc_motor_force(self, motor_value: float):
        # TODO: Figure out the proper unit and convertion
        return motor_value * self.motor_volume * MOTOR_FORCE_SCALER

    def _calc_power_consumption(self):
        # TODO: Figure out the proper unit and convertion
        return (
            (abs(self._left_motor) + abs(self._right_motor))
            * self.motor_volume
            * MOTOR_POWER_SCALER
        )

    def _calc_robot_density(self):
        return self.mass / self.total_volume
