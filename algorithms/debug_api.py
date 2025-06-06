class RobotDebugAPI:
    def __init__(self, robot):
        self._robot = robot

    def print(self, message: any, pop_up: bool = True):
        self._robot.print(message, pop_up)

    def clear_pop_up(self):
        self._robot.debug_messages.clear()