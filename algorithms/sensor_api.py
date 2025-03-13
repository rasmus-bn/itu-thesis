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

    def get_local_message(self) -> list[str]:
        return self._robot.get_local_message()



