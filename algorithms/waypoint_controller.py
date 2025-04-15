import math
from enum import Enum

from algorithms.PID import PID
from algorithms.base_controller import BaseController


class RobotState(Enum):
    FOLLOW_TRACK = 0


class WaypointController(BaseController):
    def __init__(self, counter_steering=0.0, kp=3.0, ki=0.0, kd=0.3):
        super().__init__()
        self.base_speed = 0.5
        self.counter_steering = counter_steering
        self.state = RobotState.FOLLOW_TRACK
        self.waypoint_index = 0
        # self.pid = PID(Kp=3, Ki=0.0, Kd=0.3)
        self.pid = PID(Kp=kp, Ki=ki, Kd=kd)

    def robot_start(self):
        pass

    def robot_update(self):
        if not self.sensors or not self.controls:
            raise RuntimeError("sensors or controls not available")

        if self.state == RobotState.FOLLOW_TRACK:
            self.follow_track()

    def follow_track(self):
        # Get waypoints for the track
        waypoint_distance = self.sensors.get_waypoint_distance()
        all_waypoints = self.sensors.get_all_waypoints()
        # track_order = [0, 1, 2, 5, 8, 7, 6, 3]  # Custom track 1
        # track_order = [0, 1, 4, 3]  # Custom track 2
        track_order = [0, 1, 2, 4, 6, 7, 8, 5, 2, 1, 4, 3] # Custom track 3
        track = [all_waypoints[i] for i in track_order]

        # Update waypoint index when close to the current target
        if track[self.waypoint_index].position.get_distance(self.sensors.get_robot_position()) < waypoint_distance // 4:
            self.waypoint_index = (self.waypoint_index + 1) % len(track)
            self.controls.increment_counter("waypoints_reached")

        # Primary target waypoint
        target_waypoint = track[self.waypoint_index]

        # Look ahead to the next waypoint for counter-steering
        lookahead_index = (self.waypoint_index + 1) % len(track)
        lookahead_waypoint = track[lookahead_index]

        # Compute direction vectors
        robot_pos = self.sensors.get_robot_position()
        direction_to_target = target_waypoint.position - robot_pos
        direction_to_lookahead = lookahead_waypoint.position - target_waypoint.position

        # Compute absolute angles
        target_angle = direction_to_target.angle
        lookahead_angle = direction_to_lookahead.angle
        robot_angle = self.sensors.get_robot_angle()

        # Compute angle differences
        angle_to_target = target_angle - robot_angle
        angle_to_lookahead = lookahead_angle - target_angle  # Angle change between two waypoints

        # Normalize angles to [-π, π]
        angle_to_target = (angle_to_target + math.pi) % (2 * math.pi) - math.pi
        angle_to_lookahead = (angle_to_lookahead + math.pi) % (2 * math.pi) - math.pi

        distance_to_target = track[self.waypoint_index].position.get_distance(self.sensors.get_robot_position())

        # Introduce counter-steering based on the upcoming turn
        if waypoint_distance > distance_to_target > waypoint_distance // 2:
            counter_steering = -angle_to_lookahead * self.counter_steering
        else:
            counter_steering = 0

        # Apply counter-steering to the angle difference
        adjusted_angle_difference = angle_to_target + counter_steering

        # Compute PID correction
        control = self.pid.compute(adjusted_angle_difference)

        # Convert control signal into motor values
        # base_speed *= min((distance_to_target / waypoint_distance), 1.0)  # slow down before each waypoint
        turn = max(-1, min(1, control))  # Clamp turn value to [-1, 1]

        left_motor = self.base_speed - turn
        right_motor = self.base_speed + turn

        # Apply motor values
        self.controls.set_motor_values(left_motor, right_motor)
