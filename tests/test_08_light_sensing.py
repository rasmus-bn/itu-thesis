from engine.environment import Environment, Resource
from engine.robot import RobotBase
from engine.simulation import SimulationBase
import pygame
import math

from sim_math.angles import normalize_angle

SIZE_X = 1280
SIZE_Y = 720

sim = SimulationBase(
    pixels_x=SIZE_X, pixels_y=SIZE_Y, enable_realtime=True, enable_display=True
)


class ManualRobotBase(RobotBase):
    static_count = 0

    def __str__(self):
        colors = ["Red", "Blue"]
        return f"{colors[self.num]}"

    def __init__(
        self,
        battery_capacity,
        motor_strength,
        position=(0, 0),
        angle=0,
        controller=None,
        ignore_battery=False,
        **kwargs,
    ):
        super().__init__(
            battery_capacity,
            motor_strength,
            position=position,
            angle=angle,
            controller=controller,
            ignore_battery=ignore_battery,
        )
        self.num = ManualRobotBase.static_count
        ManualRobotBase.static_count += 1

    def controller_update(self):
        motor_left = 0
        motor_right = 0

        keys = pygame.key.get_pressed()  # Get key states
        controlSchemes = [
            {
                "up": keys[pygame.K_i],
                "down": keys[pygame.K_k],
                "left": keys[pygame.K_j],
                "right": keys[pygame.K_l],
                "attach": keys[pygame.K_SPACE],
                "color": (255, 0, 0),  # Red
                "comm_range": 50,
                "message": "I'm Red.",
            },
            {
                "up": keys[pygame.K_w],
                "down": keys[pygame.K_s],
                "left": keys[pygame.K_a],
                "right": keys[pygame.K_d],
                "attach": keys[pygame.K_e],
                "color": (0, 0, 255),  # Blue
                "comm_range": 100,
                "message": "I'm Blue.",
            },
        ]

        self.color = controlSchemes[self.num]["color"]
        self._comms_range = controlSchemes[self.num]["comm_range"]
        self.set_message(controlSchemes[self.num]["message"])

        # Movement Controls (values accumulate)
        if controlSchemes[self.num]["up"]:  # Move Forward
            motor_left += 1
            motor_right += 1
        if controlSchemes[self.num]["down"]:  # Move Backward
            motor_left -= 1
            motor_right -= 1
        if controlSchemes[self.num]["left"]:  # Turn Left
            motor_left -= 0.5
            motor_right += 0.5
        if controlSchemes[self.num]["right"]:  # Turn Right
            motor_left += 0.5
            motor_right -= 0.5
        if controlSchemes[self.num]["attach"]:
            self.light_switch = not self.light_switch
            print(f"light: {self.light_switch}")

        self.set_motor_values(motor_left, motor_right)

        # print(f"Speedometer: {self.speedometer}")

        def get_waypoint_by_angle(angle: float):
            angle = normalize_angle(angle)
            dirs = ["right", "up", "left", "down"]
            direction = dirs[int((angle + (math.pi / 4)) // (math.pi / 2)) % 4]
            print(direction)
            # print(len(self.visited_waypoints))
            # neighbor = self.visited_waypoints[-1].neighbors.get(direction)
            # if neighbor is None:
            #     print("Falling back to random waypoint")
            #     neighbor = self.get_random_waypoint()
            # return neighbor

        lights = self.light_detectors.copy()
        if not lights:
            pass

        else:
            closest_light = min(lights, key=lambda x: x.distance)
            global_light_angle = self.body.angle + closest_light.angle
            get_waypoint_by_angle(global_light_angle)
            # self.target_waypoint = self.get_waypoint_by_angle(global_light_angle)
            # self.move_to_target_waypoint()
            # print(closest_light.angle)


if __name__ == "__main__":
    # Settings
    MAX_SIZE = 20000
    ROBOT_COUNT = 10
    RESOURCES_COUNT = 10

    # test the environment
    env = Environment(sim)
    env.generate_resources(5)

    # Create manual robot 1 controlled by arrow keys
    manual_robot = ManualRobotBase(
        ignore_battery=True,
        battery_capacity=100000,
        motor_strength=100000,
        position=(0, 0),
    )
    sim.add_game_object(manual_robot)

    # Create manual robot 2 controlled by wasd keys
    manual_robot = ManualRobotBase(
        ignore_battery=True,
        battery_capacity=100000,
        motor_strength=100000,
        position=(0, SIZE_Y // 4),
    )
    sim.add_game_object(manual_robot)

    sim.run()
