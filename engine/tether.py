from pygame import Surface
import pygame
import pymunk
from pymunk import Vec2d
from engine.objects import IGameObject


class Tether:
    def __init__(
            self,
            robot: IGameObject,
            resource: IGameObject,
            robot_offset: tuple[float] = None,
            resource_offset: tuple[float] = None,
    ):
        self.robot: IGameObject = robot
        self.resource: IGameObject = resource
        self.robot_offset: tuple[float] = robot_offset or (0, 0)
        self.resource_offset: tuple[float] = resource_offset or (0, 0)

        self.constraint: pymunk.Constraint = pymunk.PinJoint(
                a=self.robot.body,
                b=self.resource.body,
                anchor_a=Vec2d(*self.robot_offset),
                anchor_b=Vec2d(*self.resource_offset)
        )
        self.constraint.tether = self

    def draw(self, surface: Surface):
        pygame.draw.line(
            surface=surface,
            color=(80, 80, 80),
            start_pos=self.robot.sim.meta.pymunk_to_pygame_point(self.robot.body.local_to_world(self.robot_offset), surface),
            end_pos=self.robot.sim.meta.pymunk_to_pygame_point(self.resource.body.local_to_world(self.resource_offset), surface),
            width=3,
        )
