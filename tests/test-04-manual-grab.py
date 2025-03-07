from engine.environment import Environment, Resource
from engine.robot import RobotBase
from engine.simulation import SimulationBase
import pygame
import random
import math

SIZE_X = 1280
SIZE_Y = 720

sim = SimulationBase(pixels_x=SIZE_X, pixels_y=SIZE_Y, enable_realtime=True, enable_display=True)

class ManualRobotBase(RobotBase):
    def __init__(self, battery_capacity, motor_strength, position=(0, 0), angle=0):
        super().__init__(battery_capacity, motor_strength, position=position, angle=angle)
        self.is_attached = False

    def controller_update(self):
        keys = pygame.key.get_pressed()  # Get key states

        motor_left = 0
        motor_right = 0

        # Movement Controls (values accumulate)
        if keys[pygame.K_UP]:  # Move Forward
            motor_left += 1
            motor_right += 1
        if keys[pygame.K_DOWN]:  # Move Backward
            motor_left -= 1
            motor_right -= 1
        if keys[pygame.K_LEFT]:  # Turn Left
            motor_left -= 0.5
            motor_right += 0.5
        if keys[pygame.K_RIGHT]:  # Turn Right
            motor_left += 0.5
            motor_right -= 0.5

        if keys[pygame.K_SPACE]:
            if self.ir_sensors[2]["gameobject"] is not None:
                self.is_attached = True
                obj = self.ir_sensors[2]["gameobject"]
                if isinstance(obj, Resource):
                    self.attach_to_resource(obj)
                    print(f"attached: {obj}")
                else:
                    print(f"cannot attach: {obj}")

        self.set_motor_values(motor_left, motor_right)


# Settings
MAX_SIZE = 20000; ROBOT_COUNT = 10; RESOURCES_COUNT = 10

# test the environment
env = Environment(sim)
env.generate_resources(50)

# Create a manual robot controlled by arrow keys
manual_robot = ManualRobotBase(battery_capacity=100000, motor_strength=100000, position=(SIZE_X // 2, SIZE_Y // 2))
sim.add_game_object(manual_robot)

# # Create 5 random robots
# MAX_SIZE = 20000
# for _ in range(ROBOT_COUNT):
#     x = random.randint(0, SIZE_X)
#     y = random.randint(0, SIZE_Y)
#     angle = random.uniform(0, 2 * math.pi)
#     battery_capacity = random.randint(10, MAX_SIZE)
#     motor_strength = random.randint(10, MAX_SIZE)
#     robot = RobotBase(battery_capacity, motor_strength, position=(x, y), angle=angle)
#     sim.add_game_object(robot)
#     motor_left = 1
#     motor_right = 0.95
#     robot.set_motor_values(motor_left, motor_right)

sim.run()