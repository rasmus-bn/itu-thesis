from abc import ABC, abstractmethod

from algorithms.control_api import RobotControlAPI
from algorithms.debug_api import RobotDebugAPI
from algorithms.sensor_api import RobotSensorAPI


class BaseController(ABC):
    def __init__(self):
        self.sensors: RobotSensorAPI | None = None
        self.controls: RobotControlAPI | None = None
        self.controls: RobotDebugAPI | None = None
        self.robot_is_initialized = False
        

    def set_apis(self, sensors, controls, debug: RobotDebugAPI = None):
        self.sensors = sensors
        self.controls = controls
        self.debug = debug

    @abstractmethod
    def robot_start(self):
        pass

    @abstractmethod
    def robot_update(self):
        pass

    def update(self):
        assert self.sensors and self.controls

        if not self.robot_is_initialized:
            self.robot_start()
            self.robot_is_initialized = True

        self.robot_update()
