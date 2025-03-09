import math
import random
import time
from enum import Enum
from algorithms.base_controller import BaseController
from engine.environment import Resource


class RobotState(Enum):
    SEARCHING = 1
    RETRIEVING = 2


class RandomSearchController(BaseController):
    def __init__(self):
        super().__init__()
        self.state = RobotState.SEARCHING
        self.start_time = time.time()
        self.search_duration = 1  # seconds
        self.random_direction = (0, 0)

    def update(self):
        if not self.sensors or not self.controls:
            raise RuntimeError("sensors or controls not available")

        if self.state == RobotState.SEARCHING:
            self.search()
        elif self.state == RobotState.RETRIEVING:
            self.retrieve()

    def search(self):
        # Check for resources in lidar
        lidar_data = self.sensors.get_lidar()
        for sensor in lidar_data:
            if isinstance(sensor.gameobject, Resource): # and len(sensor.gameobject.constraints) == 0
                self.controls.attach_to_resource(sensor.gameobject)
                self.state = RobotState.RETRIEVING
                return

        # If the robot just started searching or finished a movement cycle
        if time.time() - self.start_time > self.search_duration:
            self.start_time = time.time()
            self.random_direction = (random.uniform(0.5, 1), random.uniform(0.5, 1))

        # Move in the random direction
        left_motor, right_motor = self.random_direction
        self.controls.set_motor_values(left_motor, right_motor)

    def retrieve(self):
        if not self.controls.is_attached():
            self.state = RobotState.SEARCHING
            self.search_start_time = time.time()
            return

        # Calculate the direction to the home base
        home_direction = self.sensors.homebase_direction()
        robot_angle = self.sensors.get_robot_angle()

        # Determine the angle between the robot's forward direction and the home base direction
        home_angle = math.atan2(home_direction.y, home_direction.x) + (math.pi/2)
        angle_difference = home_angle - robot_angle

        # Normalize the angle difference to be between -pi and pi
        angle_difference = (angle_difference + math.pi) % (2 * math.pi) - math.pi

        # Use the angle difference to set motor values
        if abs(angle_difference) < 0.3:  # Move forward if almost aligned
            self.controls.set_motor_values(1.0, 1.0)
        elif angle_difference > 0:
            self.controls.set_motor_values(0, 1.0)  # Turn right
        else:
            self.controls.set_motor_values(1.0, 0)  # Turn left
