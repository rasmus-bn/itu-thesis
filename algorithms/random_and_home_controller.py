import math
from enum import Enum

from algorithms.PID import PID
from algorithms.base_controller import BaseController
from engine.types import IWaypointData
from random import choice


class RobotState(Enum):
    WAIT = 0
    SEARCH = 1
    GO_HOME = 2


class RandomHomeController(BaseController):
    def __init__(self):
        super().__init__()
        self.pid = PID(Kp=7, Ki=0.2, Kd=0.4)

        # initial state
        self.state = RobotState.SEARCH

        # target waypoint
        self.target_waypoint: IWaypointData | None = None

        # list of waypoint to get back
        self.visited_waypoints: list[IWaypointData] = []

    def update(self):
        assert self.sensors and self.controls

        if self.state == RobotState.SEARCH:
            self.search()

        if self.state == RobotState.GO_HOME:
            self.go_home()

        if self.state == RobotState.WAIT:
            self.controls.set_motor_values(0,0)
            pass

    def search(self):
        waypoint_distance = self.sensors.get_waypoint_distance()
        all_waypoints = self.sensors.get_all_waypoints()
        robot_position = self.sensors.get_robot_position()

        def get_new_waypoint():
            directions = ["up", "down", "left", "right"]
            unvisited_options = []
            fallback_options = []

            # Check all directions
            for direction in directions:
                neighbor = self.target_waypoint.neighbors.get(direction)
                if neighbor is not None:
                    if neighbor not in self.visited_waypoints:
                        unvisited_options.append(neighbor)
                    else:
                        fallback_options.append(neighbor)

            if unvisited_options:
                new_target_waypoint = choice(unvisited_options)
            elif fallback_options:
                new_target_waypoint = choice(fallback_options)
            else:
                raise RuntimeError("No waypoint to target")

            self.visited_waypoints.append(new_target_waypoint)
            return new_target_waypoint

        # find at least one homebase target
        if not self.target_waypoint:
            print("Set base waypoint")
            for waypoint in all_waypoints:
                if waypoint.is_homebase:
                    self.target_waypoint = waypoint
                    self.visited_waypoints = []
                    self.visited_waypoints.append(waypoint)
                    break
        assert self.target_waypoint is not None

        if self.target_waypoint.position.get_distance(robot_position) < waypoint_distance//4:
            if len(self.visited_waypoints) >= 5:
                self.state = RobotState.GO_HOME
                self.target_waypoint = None
                return
            self.target_waypoint = get_new_waypoint()

        # Compute direction vectors
        robot_pos = self.sensors.get_robot_position()
        direction_to_target = self.target_waypoint.position - robot_pos

        # Compute absolute angles
        target_angle = direction_to_target.angle
        robot_angle = self.sensors.get_robot_angle()

        # Compute angle differences
        angle_to_target = target_angle - robot_angle

        # Normalize angles to [-π, π]
        angle_to_target = (angle_to_target + math.pi) % (2 * math.pi) - math.pi

        # Compute PID correction
        control = self.pid.compute(angle_to_target)

        # Convert control signal into motor values
        base_speed = 1.0  # Max forward speed
        turn = max(-1, min(1, control))  # Clamp turn value to [-1, 1]

        left_motor = base_speed - turn
        right_motor = base_speed + turn

        # Apply motor values
        self.controls.set_motor_values(left_motor, right_motor)

    def go_home(self):
        waypoint_distance = self.sensors.get_waypoint_distance()
        robot_position = self.sensors.get_robot_position()

        def get_new_waypoint():
            new_target_waypoint = self.visited_waypoints.pop()
            return new_target_waypoint

        if self.target_waypoint is None:
            self.target_waypoint = get_new_waypoint()

        if self.target_waypoint.position.get_distance(robot_position) < waypoint_distance // 4:
            if len(self.visited_waypoints) == 0:
                self.state = RobotState.WAIT
                self.target_waypoint = None
                return
            self.target_waypoint = get_new_waypoint()

        # Compute direction vectors
        robot_pos = self.sensors.get_robot_position()
        direction_to_target = self.target_waypoint.position - robot_pos

        # Compute absolute angles
        target_angle = direction_to_target.angle
        robot_angle = self.sensors.get_robot_angle()

        # Compute angle differences
        angle_to_target = target_angle - robot_angle

        # Normalize angles to [-π, π]
        angle_to_target = (angle_to_target + math.pi) % (2 * math.pi) - math.pi

        # Compute PID correction
        control = self.pid.compute(angle_to_target)

        # Convert control signal into motor values
        base_speed = 1.0  # Max forward speed
        turn = max(-1, min(1, control))  # Clamp turn value to [-1, 1]

        left_motor = base_speed - turn
        right_motor = base_speed + turn

        # Apply motor values
        self.controls.set_motor_values(left_motor, right_motor)
