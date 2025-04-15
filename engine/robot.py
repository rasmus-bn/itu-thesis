import pygame

from algorithms.control_api import RobotControlAPI
from algorithms.debug_api import RobotDebugAPI
from algorithms.sensor_api import RobotSensorAPI
from engine.battery import Battery
from engine.debug_colors import IColor
from engine.motor import AcMotor
from engine.simulation import SimulationBase
from engine.tether import Tether
from engine.gpt_generated.closest_point_on_circle import closest_point_on_circle
from engine.environment import Resource
from engine.objects import Circle
from sim_math.angles import calc_relative_angle
import numpy as np
import pymunk
from pymunk import Vec2d
from time import time

from engine.types import (
    DebugMessage,
    IBattery,
    IComponent,
    ILidarData,
    ILightData,
    IMotor,
    IRobotSpec,
)
from sim_math.units import Speed


class RobotBase(Circle):
    _robot_counter = 1  # Keeps track of unique robot IDs

    def __init__(
        self,
        robot_spec: IRobotSpec,
        sim: SimulationBase,
        position: tuple = None,
        angle: float = 0,
        color: tuple = None,
        num_ir_sensors: int = 8,
        sensor_range: float = 50.0,
        controller: any = None,
        ignore_battery: bool = False,
        robot_collision: bool = True,
        debug_color: IColor = None,
    ):
        self.spec = robot_spec
        self._comms_range = 50

        self.message: None | str = None
        self.received_messages: list[str] = []

        self._light_range = 200
        self.light_switch = False
        self.light_detectors: list[ILightData] = []

        # Debugging
        self.debug_color: IColor = debug_color
        self.debug_messages: list[DebugMessage] = []

        self.up_color = color or (255, 0, 0)

        if debug_color:
            self.up_color = debug_color.rgb

        die_color_scaler = 0.3
        self.down_color = (
            max(min(int(self.up_color[0] * die_color_scaler), 255), 0),
            max(min(int(self.up_color[1] * die_color_scaler), 255), 0),
            max(min(int(self.up_color[2] * die_color_scaler), 255), 0),
        )

        self.tether: Tether | None = None

        position = (0, 0) if position is None else position

        # Call the circle constructor
        super().__init__(
            x=position[0],
            y=position[1],
            angle=angle,
            radius=self.spec.robot_diameter.base_unit / 2,
            color=self.up_color,
            density=self.spec.robot_density_2d.base_unit,
            sim=sim,
        )

        # DC battery
        self.battery: IBattery = Battery(
            meta=sim.meta,
            body=self.body,
            capacity__wh=self.spec.battery_capacity__wh,
            infinite_power=ignore_battery,
        )
        # Left AC Motor
        self.motor_l: IMotor = AcMotor(
            meta=sim.meta,
            battery=self.battery,
            body=self.body,
            max_torque=self.spec.max_motor_torque,
            max_voltage=self.spec.max_motor_voltage,
            wheel_position=self.top,
            wheel_radius=self.spec.wheel_radius,
        )
        # Right AC Motor
        self.motor_r: IMotor = AcMotor(
            meta=sim.meta,
            battery=self.battery,
            body=self.body,
            max_torque=self.spec.max_motor_torque,
            max_voltage=self.spec.max_motor_voltage,
            wheel_position=self.bottom,
            wheel_radius=self.spec.wheel_radius,
        )
        # List of all IComponents
        self.components: list[IComponent] = [self.battery, self.motor_l, self.motor_r]

        # Speedometer
        self.speedometer = Speed.in_base_unit(0)

        # Purely for visualization
        self._wheel_size = 4
        self._wheel_pos_left = (
            self.motor_l.wheel_position[0],
            self.motor_l.wheel_position[1] - self._wheel_size,
        )
        self._wheel_pos_right = (
            self.motor_r.wheel_position[0],
            self.motor_r.wheel_position[1] + self._wheel_size,
        )

        # Sensor setup
        self.num_ir_sensors = num_ir_sensors
        self._lidar_range = sensor_range
        self.ir_sensors: list[ILidarData] = self._initialize_ir_sensors()

        # Set up the shape filter (ignores itself but detects other objects)
        self.robot_group = RobotBase._robot_counter
        RobotBase._robot_counter += 1

        robot_mask = 0b0001 if robot_collision else 0b0000
        resource_mask = 0b0100 if robot_collision else 0b0000

        self.shape.filter = pymunk.ShapeFilter(
            categories=0b0001,  # This object is a robot
            mask=robot_mask
            | 0b0010
            | resource_mask,  # Detects robots, obstacles, and goals
            group=self.robot_group,  # Ignores itself
        )

        # Create API objects
        sensors = RobotSensorAPI(self)
        controls = RobotControlAPI(self)
        debug = RobotDebugAPI(self)

        # Assign APIs to the controller
        self.controller = controller
        if controller:
            self.controller.set_apis(sensors, controls, debug)

    def set_motor_values(self, left: float, right: float):
        self.motor_l.request_force_scaled(force_scaler=left)
        self.motor_r.request_force_scaled(force_scaler=right)

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
                    distance_cm = body.position.get_distance(self.body.position)
                    # distance = result.distance
                    angle = calc_relative_angle(
                        subject_pos=body.position,
                        subject_angle=body.angle,
                        target_pos=self.body.position,
                    )
                    # Add the emitter to the target's detections
                    robot.light_detectors.append(ILightData(distance_cm, angle))

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

        # Update speedometer
        dist_moved: Vec2d = self.body.velocity
        direction_vector = Vec2d(1, 0).rotated(self.body.angle)
        dist_travelled = dist_moved.dot(direction_vector)
        self.speedometer = Speed.in_base_unit(dist_travelled)

        # if self.battery.capacity__wh > :

        # Other IComponents
        for component in self.components:
            component.preupdate()

    def postupdate(self):
        self.light_detectors.clear()
        self.received_messages.clear()

        # Delete pop-up message after 5 seconds
        while self.debug_messages:
            oldest = self.debug_messages[0]
            if time() < oldest.timestamp + 5:
                break
            self.debug_messages.pop(0)

        # Other IComponents
        for component in self.components:
            component.postupdate()

    def print(self, message: any, pop_up: bool = False):
        # Print in terminal with color
        if False:
            if self.debug_color:
                self.debug_color.print(message)
            # Print normally
            else:
                print(message)
        # Display in-game pop up text
        if pop_up:
            latest = self.debug_messages[-1] if self.debug_messages else None
            if latest and latest.message == message:
                return
            self.debug_messages.append(DebugMessage(message=message))

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
            ray_color = (
                (255, 0, 0) if sensor.distance < self._lidar_range else (0, 255, 0)
            )

            # Convert Pymunk coordinates to Pygame coordinates
            start_pos = (int(sensor_pos[0]), int(sensor_pos[1]))
            end_pos = (int(sensor_end[0]), int(sensor_end[1]))

            start_pos = self.sim.meta.pymunk_to_pygame_point(start_pos, screen)
            end_pos = self.sim.meta.pymunk_to_pygame_point(end_pos, screen)

            # Draw sensor ray
            pygame.draw.line(screen, ray_color, start_pos, end_pos, 2)

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
                    self.sim.meta.pymunk_to_pygame_point(self.body.position, screen),
                    self.sim.meta.pymunk_to_pygame_point(end_pos, screen),
                    2,
                )

    def send_your_message(self):
        pass
        # todo: implement local communication

    def draw(self, surface):
        super().draw(surface)

        # Draw direction
        right_up = self.body.local_to_world((self.right[0], self.right[1] + 1))
        right_down = self.body.local_to_world((self.right[0], self.right[1] - 1))
        center_up = self.body.local_to_world((0, +1))
        center_down = self.body.local_to_world((0, -1))
        pygame.draw.polygon(
            surface,
            (0, 255, 0),
            [
                self.sim.meta.pymunk_to_pygame_point(center_up, surface),
                self.sim.meta.pymunk_to_pygame_point(center_down, surface),
                self.sim.meta.pymunk_to_pygame_point(right_down, surface),
                self.sim.meta.pymunk_to_pygame_point(right_up, surface),
            ],
        )

        # Draw light emitter
        if self.light_switch:
            x, y = self.sim.meta.pymunk_to_pygame_point(
                self.body.position, surface=surface
            )
            pygame.draw.circle(
                surface=surface,
                color=(255, 255, 0),
                center=(x, y),
                radius=self.sim.meta.pymunk_to_pygame_scale(self._light_range),
                width=1,
            )

        # Display in-game text pop-up
        if self.debug_messages:
            font = pygame.font.SysFont(None, 24)
            font_color = self.debug_color.rgb if self.debug_color else (255, 255, 255)
            messages = self.debug_messages.copy()
            messages.reverse()
            messages = " | ".join([m.message for m in messages])
            text_surface = font.render(str(messages), True, font_color)
            text_rect = text_surface.get_rect()
            text_pos = self.sim.meta.pymunk_to_pygame_point(
                point=(
                    self.body.position.x + self.spec.robot_diameter.base_unit // 2 + 10,
                    self.body.position.y,
                ),
                surface=surface,
            )
            text_rect.midleft = text_pos
            surface.blit(text_surface, text_rect)

        # Other IComponents
        for component in self.components:
            component.draw(surface=surface)

        # Other IComponents
        for component in self.components:
            component.draw_debug(surface=surface)

    def update(self):
        # todo change
        self.controller_update()
        if self.controller:
            self.controller.update()

        # Other IComponents
        for component in self.components:
            component.update()

        forward = pymunk.Vec2d(1, 0).rotated(self.body.angle)
        velocity_along_forward = self.body.velocity.dot(forward)
        self.body.velocity = forward.normalized() * velocity_along_forward

    def controller_update(self):
        pass
