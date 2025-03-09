import math
from dataclasses import dataclass
from pygame import Surface
import pygame
import pymunk

from engine.helpers import pymunk_to_pygame_point
from typing import TYPE_CHECKING
if TYPE_CHECKING: from engine.simulation import SimulationBase


class IGameObject:
    def __init__(
        self,
        body: pymunk.Body,
        shape: pymunk.Shape,
        density: float = 1,
        virtual_height: float = 1,
    ):
        self.body = body
        self.shape = shape
        self.density = density
        self.virtual_height = virtual_height
        self.sim: SimulationBase = None

    @property
    def density_3d(self):
        return self.density * self.virtual_height

    @property
    def has_update(self):
        return getattr(self.__class__, "update") is not getattr(IGameObject, "update")

    def update(self):
        pass

    def draw(self, surface: Surface):
        raise NotImplementedError()

    def distance_to_obj_center(self, obj):
        return self.body.position.get_distance(obj.body.position)


@dataclass
class Box(IGameObject):
    x: int = 0
    y: int = 0
    angle: float = 0
    width: int = 10
    length: int = 10
    color: tuple = (255, 255, 255)
    density: int = 1
    virtual_height: int = 1
    trigger: bool = False

    def __post_init__(self):
        self.body = pymunk.Body()
        self.body.gameobject = self
        self.body.position = (self.x, self.y)
        self.body.angle = self.angle
        self.shape = pymunk.Poly.create_box(self.body, (self.width, self.length))
        self.shape.sensor = self.trigger
        IGameObject.__init__(
            self,
            body=self.body,
            shape=self.shape,
            density=self.density,
            virtual_height=self.virtual_height,
        )
        self.shape.density = self.density_3d
        self.top = (0, self.length / 2)
        self.bottom = (0, self.length / 2)
        self.left = (-self.width / 2, 0)
        self.right = (self.width / 2, 0)

    def draw(self, surface):
        # Calculate the vertices of the rotated box
        vertices = self.shape.get_vertices()
        points = []

        for vertex in vertices:
            rotated_point = self.body.local_to_world(vertex)
            points.append(pymunk_to_pygame_point(rotated_point, surface))

        # Draw the polygon
        pygame.draw.polygon(surface, self.color, points)


@dataclass
class Circle(IGameObject):
    x: int = 0
    y: int = 0
    radius: int = 10
    color: tuple = (255, 255, 255)
    density: int = 1
    virtual_height: int = 1

    def __post_init__(self):
        self.body = pymunk.Body()
        self.body.gameobject = self
        self.body.position = (self.x, self.y)
        self.shape = pymunk.Circle(self.body, self.radius)
        IGameObject.__init__(
            self,
            body=self.body,
            shape=self.shape,
            density=self.density,
            virtual_height=self.virtual_height,
        )
        self.shape.density = self.density_3d

    def draw(self, surface):
        x, y = pymunk_to_pygame_point(self.body.position, surface)
        pygame.draw.circle(
            surface,
            self.color,
            (int(x), int(y)),
            int(self.radius),
        )
