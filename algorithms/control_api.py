from engine.environment import Resource


class RobotControlAPI:

    def __init__(self, robot):
        self._robot = robot

    # Motors
    def set_motor_values(self, left: float, right: float):
        self._robot.set_motor_values(left, right)

    # Manipulator
    def attach_to_resource(self, resource: Resource):
        self._robot.attach_to_resource(resource)

    def detach_from_resource(self):
        self._robot.detach_from_resource()

    def is_attached(self):
        return self._robot.tether is not None

    def set_message(self, message: str):
        return self._robot.set_message(message=message)

    def enable_light(self):
        self._robot.light_switch = True

    def disable_light(self):
        self._robot.light_switch = False

    def toggle_light(self):
        self._robot.light_switch = not self._robot.light_switch