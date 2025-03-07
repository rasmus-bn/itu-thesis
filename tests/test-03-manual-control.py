from engine.environment import Environment
from engine.robot import RobotBase
from engine.simulation import SimulationBase
import pygame

SIZE_X = 1280
SIZE_Y = 720

sim = SimulationBase(pixels_x=SIZE_X, pixels_y=SIZE_Y, enable_realtime=True, enable_display=True)


class ManualRobotBase(RobotBase):
    def __init__(self, battery_capacity, motor_strength, position=(0, 0), angle=0):
        super().__init__(battery_capacity, motor_strength, position=position, angle=angle)

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

        # motor_left = 1
        # motor_right = 1
        # Apply the accumulated motor values
        self.set_motor_values(motor_left, motor_right)


# Settings
MAX_SIZE = 20000; ROBOT_COUNT = 100; RESOURCES_COUNT = 50

# test the environment
env = Environment(sim)
env.generate_resources(50)

# Create a manual robot controlled by arrow keys
manual_robot = ManualRobotBase(battery_capacity=100000, motor_strength=100000, position=(SIZE_X // 2, SIZE_Y // 2))
sim.add_game_object(manual_robot)

sim.run()