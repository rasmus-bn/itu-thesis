from dataclasses import dataclass
from pygame import Surface
import pygame
import pymunk

from pymunk import Vec2d
from engine.helpers import pymunk_to_pygame_point
from engine.objects import IGameObject


@dataclass
class IConstraint:
    constraint: pymunk.Constraint
    alive: bool = True

    def destroy(self):
        self.alive = False

    def draw(self, surface: Surface):
        raise NotImplementedError()


class PinJoint(IConstraint):
    def __init__(
        self,
        obj1: IGameObject,
        obj2: IGameObject,
        obj1_offset: tuple[float] = None,
        obj2_offset: tuple[float] = None,
    ):
        self.obj1: IGameObject = obj1
        self.obj2: IGameObject = obj2
        self.obj1_offset: tuple[float] = obj1_offset or (0, 0)
        self.obj2_offset: tuple[float] = obj2_offset or (0, 0)

        # Call super constructor
        IConstraint.__init__(
            self,
            pymunk.PinJoint(
                a=self.obj1.body,
                b=self.obj2.body,
                anchor_a=Vec2d(*self.obj1_offset),
                anchor_b=Vec2d(*self.obj2_offset),
            ),
        )

    def draw(self, surface: Surface):
        pygame.draw.line(
            surface=surface,
            color=(255, 255, 255),
            start_pos=pymunk_to_pygame_point(
                point=self.obj1.body.local_to_world(self.obj1_offset), surface=surface
            ),
            end_pos=pymunk_to_pygame_point(
                point=self.obj2.body.local_to_world(self.obj2_offset), surface=surface
            ),
            width=2,
        )
