from engine.environment import Environment, Resource
from engine.robot import RobotBase
from engine.robot_spec import RobotSpec
from engine.simulation import SimulationBase
import pygame

from sim_math.units import Mass

SIZE_X = 1280
SIZE_Y = 720

sim = SimulationBase(
    pixels_x=SIZE_X, pixels_y=SIZE_Y, enable_realtime=True, enable_display=True
)


class ManualRobotBase(RobotBase):
    static_count = 0

    def __init__(
        self,
        robot_spec: RobotSpec,
        position=(0, 0),
        angle=0,
        controller=None,
        ignore_battery=False,
        **kwargs,
    ):
        super().__init__(
            robot_spec=robot_spec,
            sim=sim,
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
            # {
            #     "up": keys[pygame.K_UP],
            #     "down": keys[pygame.K_DOWN],
            #     "left": keys[pygame.K_LEFT],
            #     "right": keys[pygame.K_RIGHT],
            #     "attach": keys[pygame.K_SPACE],
            # },
            {
                "up": keys[pygame.K_w],
                "down": keys[pygame.K_s],
                "left": keys[pygame.K_a],
                "right": keys[pygame.K_d],
                "attach": keys[pygame.K_e],
            },
        ]

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
            if self.ir_sensors[2].gameobject is not None:
                obj = self.ir_sensors[2].gameobject
                if isinstance(obj, Resource):
                    self.attach_to_resource(obj)
                else:
                    print(f"cannot attach: {obj}")

        self.set_motor_values(motor_left, motor_right)


if __name__ == "__main__":
    # Settings
    MAX_SIZE = 20000
    ROBOT_COUNT = 10
    RESOURCES_COUNT = 10

    # test the environment
    env = Environment(sim)
    env.generate_resources(5)

    robot_spec = RobotSpec(
        meta=sim.meta,
        battery_mass=Mass.in_kg(537),
        motor_mass=Mass.in_kg(51),
    )
    print(robot_spec.get_spec_sheet())

    # Create manual robot 1 controlled by arrow keys
    manual_robot = ManualRobotBase(
        robot_spec=robot_spec,
        position=(0, 0),
    )

    # # Create manual robot 2 controlled by wasd keys
    # manual_robot = ManualRobotBase(
    #     robot_spec=robot_spec,
    #     position=(0, 0),
    # )

    sim.run()
