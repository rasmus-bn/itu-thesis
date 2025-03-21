import math
from enum import Enum, auto
from algorithms.PID import PID
from algorithms.base_controller import BaseController
from engine.environment import Resource
from engine.types import IWaypointData
from random import choice, uniform
from sim_math.angles import normalize_angle


class RobotState(Enum):
    WAIT = auto()
    SEARCH = auto()
    RETRIEVE = auto()
    JOIN = auto()


class RandomRecruitController(BaseController):
    def __init__(self):
        super().__init__()

        # local robot variables
        self.state = RobotState.SEARCH  # initial state
        self.target_waypoint: IWaypointData | None = None
        self.visited_waypoints: list[IWaypointData] = []
        self.max_speed = 0.0
        self.RECRUITMENT_THRESHOLD = 1 / 5  # speed threshold where the robot will start recruiting
        self.PID = PID(Kp=7, Ki=0.2, Kd=0.4)
        self.BASE_SPEED = 1.0

        # variables needed to be initialized
        self.HOME_BASE_WAYPOINT = None
        self.ALL_WAYPOINTS = None
        self.WAYPOINT_GAP = None

    def robot_start(self):
        self.WAYPOINT_GAP = self.sensors.get_waypoint_distance()
        self.ALL_WAYPOINTS = self.sensors.get_all_waypoints()
        self.HOME_BASE_WAYPOINT = self.find_home_base_waypoint()

    def switch_state(self, state: RobotState):
        self.target_waypoint = None
        self.state = state

    def robot_update(self):
        self.max_speed = max(self.max_speed, self.sensors.get_robot_speed())  # update max speed

        if self.state == RobotState.WAIT: self.controls.set_motor_values(0, 0)
        if self.state == RobotState.SEARCH: self.search()
        if self.state == RobotState.RETRIEVE: self.retrieve()
        if self.state == RobotState.JOIN: self.join()

    def search(self):
        robot_position = self.sensors.get_robot_position()
        self.controls.disable_light()

        # go home
        if not self.visited_waypoints or not self.target_waypoint:
            self.visited_waypoints.append(self.HOME_BASE_WAYPOINT)
            self.target_waypoint = self.HOME_BASE_WAYPOINT

        # check if a resource is found
        lidar_data = self.sensors.get_lidar()
        for sensor in lidar_data:
            if isinstance(sensor.gameobject, Resource):
                self.controls.attach_to_resource(sensor.gameobject)
                return self.switch_state(RobotState.RETRIEVE)

        # if arrived at the waypoint, get new waypoint
        if self.target_waypoint.position.get_distance(robot_position) < self.WAYPOINT_GAP // 4:
            self.visited_waypoints.append(self.target_waypoint)
            self.target_waypoint = self.get_random_waypoint()

        # check if recruited
        if self.sensors.get_light_detectors() and len(self.visited_waypoints) != 0:
            return self.switch_state(RobotState.JOIN)

        self.move_to_target_waypoint()

    def retrieve(self):
        robot_position = self.sensors.get_robot_position()

        # recruit other robots
        if self.sensors.get_robot_speed() < self.max_speed * self.RECRUITMENT_THRESHOLD:
            self.controls.enable_light()
        else:
            self.controls.disable_light()

        # share path with other robots
        path_str = "retrieve:" + "|".join([waypoint.to_message() for waypoint in self.visited_waypoints])
        self.controls.set_message(message=path_str)
        self.debug.print(message=path_str, pop_up=True)

        # compare to other paths
        messages = self.sensors.get_received_messages()
        for message in messages:
            if message is None:
                continue
            if message.startswith("retrieve:"):
                if message == path_str: continue  # ignore if own path
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

        # when the state is first switched
        if self.target_waypoint is None:
            self.target_waypoint = self.get_next_waypoint_home()

        # move to next waypoint on the way to home base
        if self.target_waypoint.position.get_distance(robot_position) < self.WAYPOINT_GAP // 4:
            if len(self.visited_waypoints) == 0:
                return self.switch_state(RobotState.SEARCH)
            self.target_waypoint = self.get_next_waypoint_home()

        self.move_to_target_waypoint()

    def join(self):
        print("joining forces")
        lights = self.sensors.get_light_detectors()
        if not lights:
            return self.switch_state(RobotState.SEARCH)

        closest_light = min(lights, key=lambda x: x.distance)
        global_light_angle = self.sensors.get_robot_angle() + closest_light.angle
        self.target_waypoint = self.get_waypoint_by_angle(global_light_angle)
        self.move_to_target_waypoint()

    def get_random_waypoint(self) -> IWaypointData:
        directions = ["up", "down", "left", "right"]
        unvisited_options = []
        fallback_options = []
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
            raise RuntimeError("no waypoint to target")
        return new_target_waypoint

    def get_waypoint_by_angle(self, angle: float) -> IWaypointData:
        angle = normalize_angle(angle)
        dirs = ["right", "up", "left", "down"]
        direction = dirs[int((angle + (math.pi / 4)) // (math.pi / 2)) % 4]
        print(len(self.visited_waypoints))
        neighbor = self.visited_waypoints[-1].neighbors.get(direction)
        if neighbor is None:
            print("Falling back to random waypoint")
            neighbor = self.get_random_waypoint()
        return neighbor

    def find_home_base_waypoint(self) -> IWaypointData:
        for waypoint in self.ALL_WAYPOINTS:
            if waypoint.is_homebase:
                return waypoint
        raise RuntimeError("cannot find any home base waypoint")

    def get_next_waypoint_home(self):
        new_target_waypoint = self.visited_waypoints.pop()
        return new_target_waypoint

    def move_to_target_waypoint(self):
        # Compute direction vectors
        robot_pos = self.sensors.get_robot_position()
        direction_to_target = self.target_waypoint.position - robot_pos
        # Compute absolute angles
        target_angle = direction_to_target.angle
        robot_angle = self.sensors.get_robot_angle()
        angle_to_target = target_angle - robot_angle  # Compute angle differences
        angle_to_target = (angle_to_target + math.pi) % (2 * math.pi) - math.pi  # Normalize angles to [-π, π]
        # Apply the movement
        control = self.PID.compute(angle_to_target)  # Compute PID correction
        turn = max(-1, min(1, control))  # Clamp turn value to [-1, 1]
        left_motor = self.BASE_SPEED - turn
        right_motor = self.BASE_SPEED + turn
        self.controls.set_motor_values(left_motor, right_motor)
