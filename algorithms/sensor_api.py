from engine.types import IWaypointData


class RobotSensorAPI:

    def __init__(self, robot):
        self._robot = robot

    def get_lidar(self):
        return self._robot.ir_sensors

    def homebase_direction(self):
        homebase = self._robot.sim.environment.get_homebase()
        return (self._robot.body.position - homebase.body.position).normalized()

    def get_robot_angle(self) -> float:
        return self._robot.body.angle

    def get_robot_position(self) -> float:
        return self._robot.body.position

    def get_received_messages(self) -> list[str]:
        return self._robot.get_received_messages()

    def get_all_waypoints(self) -> list[IWaypointData]:
        return self._robot.sim.environment.get_all_waypoints()

    def get_waypoint_distance(self) -> float:
        return self._robot.sim.environment.get_waypoint_distance()

    def get_robot_light_input(self) -> float:
        return self._robot.light_detectors.copy()

    def get_robot_speed(self) -> float:
        return self._robot.speedometer
