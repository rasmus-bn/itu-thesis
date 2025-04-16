from pymunk import vec2d
from engine.types import ILightData, IWaypointData
from sim_math.units import Speed
from typing import TYPE_CHECKING

if TYPE_CHECKING: from engine.robot import RobotBase


class RobotSensorAPI:
    def __init__(self, robot):
        self._robot: RobotBase = robot

    def get_lidar(self):
        return self._robot.ir_sensors

    def homebase_direction(self):
        homebase = self._robot.sim.environment.get_homebase()
        return (self._robot.body.position - homebase.body.position).normalized()

    def get_robot_angle(self) -> float:
        return self._robot.body.angle

    def get_robot_position(self) -> vec2d:
        return self._robot.body.position

    def get_received_messages(self) -> list[str]:
        return self._robot.get_received_messages()

    def get_all_waypoints(self) -> list[IWaypointData]:
        return self._robot.sim.environment.get_all_waypoints()

    def get_waypoints_dict(self) -> dict[str, IWaypointData]:
        return self._robot.sim.environment.get_waypoints_dict()

    def get_waypoint_distance(self) -> float:
        return self._robot.sim.environment.get_waypoint_distance()

    def get_light_detectors(self) -> list[ILightData]:
        return self._robot.light_detectors.copy()

    def get_robot_speed(self) -> Speed:
        return self._robot.speedometer

    def get_robot_diameter(self) -> float:
        return self._robot.spec.robot_diameter.base_unit
