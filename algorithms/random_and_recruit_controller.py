import math
from enum import Enum, auto

from algorithms.PID import PID
from algorithms.base_controller import BaseController
from engine.environment import Resource
from engine.types import IWaypointData
from random import choice, uniform

from sim_math.angles import normalize_angle

QUATER_PI = math.pi / 4
THREE_QUATER_PI = 3 * math.pi / 4
ONE_AND_QUATER_PI = 1 + QUATER_PI
ONE_AND_THREE_QUATER_PI = 1 + THREE_QUATER_PI


class RobotState(Enum):
    WAIT = auto()
    SEARCH = auto()
    JOINING_FORCE = auto()
    RETRIEVE = auto()


class RandomRecruitController(BaseController):
    def __init__(self):
        super().__init__()
        self.pid = PID(Kp=7, Ki=0.2, Kd=0.4)

        # initial state
        self.state = RobotState.SEARCH

        # target waypoint
        self.target_waypoint: IWaypointData | None = None

        # list of waypoint to get back
        self.visited_waypoints: list[IWaypointData] = []

        # max speed
        self.max_speed = 0

        # speed threshold where the robot will start recruiting
        self.recruitment_threshold = 1 / 5


    def update(self):
        assert self.sensors and self.controls

        if self.sensors.get_robot_speed() > self.max_speed:
            self.max_speed = self.sensors.get_robot_speed()

        if self.state == RobotState.SEARCH:
            self.search()

        if self.state == RobotState.RETRIEVE:
            self.retrieve()

        if self.state == RobotState.WAIT:
            self.controls.set_motor_values(0, 0)
            pass

    def get_random_waypoint(self) -> IWaypointData:
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

    def get_waypoint_by_angle(self, angle: float) -> IWaypointData:
        angle = normalize_angle(angle)

        waypoint_direction: str = "right"
        if angle > QUATER_PI and angle <= THREE_QUATER_PI:
            waypoint_direction = "up"
        elif angle > THREE_QUATER_PI and angle <= ONE_AND_QUATER_PI:
            waypoint_direction = "left"
        elif angle > ONE_AND_QUATER_PI and angle <= ONE_AND_THREE_QUATER_PI:
            waypoint_direction = "down"

        neighbor = self.target_waypoint.neighbors.get(waypoint_direction)

        # w = self.target_waypoint
        if neighbor is None:
            print("Falling back to random waypoint")
            neighbor = self.get_random_waypoint()

        return neighbor

    def join_force(self):
        self.controls.disable_light()

    def detect_resource(self) -> Resource | None:
        # Check for resources in lidar
        lidar_data = self.sensors.get_lidar()
        for sensor in lidar_data:
            if isinstance(
                sensor.gameobject, Resource
            ):  # and len(sensor.gameobject.constraints) == 0
                return sensor.gameobject
        return None

    def move_toward_waypoint(self):
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

    def search(self):
        self.controls.disable_light()
        waypoint_distance = self.sensors.get_waypoint_distance()
        all_waypoints = self.sensors.get_all_waypoints()
        robot_position = self.sensors.get_robot_position()

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

        # Check for resources in lidar
        resource = self.detect_resource()
        if resource:
            self.controls.attach_to_resource(resource)
            self.state = RobotState.RETRIEVE
            return

        if (
            self.target_waypoint.position.get_distance(robot_position)
            < waypoint_distance // 4
        ):
            if len(self.visited_waypoints) >= 50:
                self.state = RobotState.RETRIEVE
                self.target_waypoint = None
                return
            self.target_waypoint = self.get_random_waypoint()

        # check for call for help
        lights = self.sensors.get_light_detectors()
        if lights:
            closest_light = min(lights, key=lambda x: x.distance)
            print("joining forces")
            global_light_angle = self.sensors.get_robot_angle() + closest_light.angle
            self.target_waypoint = self.get_waypoint_by_angle(global_light_angle)

        self.move_toward_waypoint()

    def get_next_waypoint_home(self):
        new_target_waypoint = self.visited_waypoints.pop()
        return new_target_waypoint

    def retrieve(self):
        waypoint_distance = self.sensors.get_waypoint_distance()
        robot_position = self.sensors.get_robot_position()

        # recruit other robots
        if self.sensors.get_robot_speed() < self.max_speed * self.recruitment_threshold:
            self.controls.enable_light()
        else:
            self.controls.disable_light()

        # share path with other robots
        path_str = "retrieve:" + "|".join(
            [waypoint.to_message() for waypoint in self.visited_waypoints]
        )
        self.controls.set_message(message=path_str)

        # compare to other paths
        messages = self.sensors.get_received_messages()
        for message in messages:
            if message is None:
                continue
            if message.startswith("retrieve:"):
                # ignore if own path
                if message == path_str:
                    continue

                message = message.replace("retrieve:", "")

                # ignore if other robot got home
                if message == "":
                    continue
                other_path = message.split("|")
                other_path = [IWaypointData.from_message(wp) for wp in other_path]
                if len(other_path) == len(self.visited_waypoints):
                    if uniform(0, 1) > 0.2:
                        print("Adopting other path, by chance")
                        self.visited_waypoints = other_path
                if len(other_path) < len(self.visited_waypoints):
                    print("Adopting other path")
                    self.visited_waypoints = other_path

        # go home logic vv

        if self.target_waypoint is None:
            self.target_waypoint = self.get_next_waypoint_home()

        if (
            self.target_waypoint.position.get_distance(robot_position)
            < waypoint_distance // 4
        ):
            if len(self.visited_waypoints) == 0:
                self.state = RobotState.SEARCH
                self.target_waypoint = None
                return
            self.target_waypoint = self.get_next_waypoint_home()

        self.move_toward_waypoint()
