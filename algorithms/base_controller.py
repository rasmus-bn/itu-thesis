from abc import ABC, abstractmethod

from algorithms.control_api import RobotControlAPI
from algorithms.sensor_api import RobotSensorAPI


class BaseController(ABC):
    def __init__(self):
        self.sensors: RobotSensorAPI | None = None
        self.controls: RobotControlAPI | None = None

    def set_apis(self, sensors, controls):
        self.sensors = sensors
        self.controls = controls

    @abstractmethod
    def update(self):
        pass
