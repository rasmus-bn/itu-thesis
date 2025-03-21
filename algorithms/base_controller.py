from abc import ABC, abstractmethod

from algorithms.control_api import RobotControlAPI
from algorithms.debug_api import RobotDebugAPI
from algorithms.sensor_api import RobotSensorAPI


class BaseController(ABC):
    def __init__(self):
        self.sensors: RobotSensorAPI | None = None
        self.controls: RobotControlAPI | None = None
        self.controls: RobotDebugAPI | None = None

    def set_apis(self, sensors, controls, debug: RobotDebugAPI = None):
        self.sensors = sensors
        self.controls = controls
        self.debug = debug

    @abstractmethod
    def update(self):
        pass
