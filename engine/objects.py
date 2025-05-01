import math
from dataclasses import dataclass
try:
    import pygame
    from pygame import Surface
except ImportError:
    class Surface: pass
import pymunk

from typing import TYPE_CHECKING
if TYPE_CHECKING: from engine.simulation import SimulationBase


class IGameObject:
    def __init__(
        self,
        body: pymunk.Body,
        shape: pymunk.Shape,
        density: float = 1,
        virtual_height: float = 1,
        sim: "SimulationBase" = None,
    ):
        self.body: pymunk.Body = body
        self.shape: pymunk.Shape = shape
        self.density = density
        self.virtual_height = virtual_height
        self.sim: "SimulationBase" = sim
        if self.sim is not None:
            self.sim.add_game_object(self)

    @property
    def density_3d(self):
        return self.density * self.virtual_height

    @property
    def has_update(self):
        return getattr(self.__class__, "update") is not getattr(IGameObject, "update")

    def preupdate(self):
        pass

    def update(self):
        pass

    def postupdate(self):
        pass

    def draw(self, surface: Surface):
        raise NotImplementedError()

    def distance_to_obj_center(self, obj):
        return self.body.position.get_distance(obj.body.position)


@dataclass
class Box(IGameObject):
    x: float = 0
    y: float = 0
    angle: float = 0
    width: float = 10
    length: float = 10
    color: tuple = (255, 255, 255)
    density: float = 1
    virtual_height: float = 1
    trigger: bool = False
    sim: "SimulationBase" = None

    def __post_init__(self):
        self.body: pymunk.Body = pymunk.Body()
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
            sim=self.sim,
        )
        self.shape.density = self.density_3d
        self.top = (0, self.length / 2)
        self.bottom = (0, -self.length / 2)
        self.left = (-self.width / 2, 0)
        self.right = (self.width / 2, 0)

    def draw(self, surface):
        # Calculate the vertices of the rotated box
        vertices = self.shape.get_vertices()
        points = []

        for vertex in vertices:
            rotated_point = self.body.local_to_world(vertex)
            points.append(self.sim.meta.pymunk_to_pygame_point(rotated_point, surface))

        # Draw the polygon
        pygame.draw.polygon(surface, self.color, points)

@dataclass
class Circle(IGameObject):
    x: float = 0
    y: float = 0
    angle: float = 0
    radius: float = 10
    color: tuple = (255, 255, 255)
    density: float = 1
    virtual_height: float = 1
    trigger: bool = False
    sim: "SimulationBase" = None

    def __post_init__(self):
        self.body = pymunk.Body()
        self.body.gameobject = self
        self.body.position = (self.x, self.y)
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.sensor = self.trigger
        IGameObject.__init__(
            self,
            body=self.body,
            shape=self.shape,
            density=self.density,
            virtual_height=self.virtual_height,
            sim=self.sim,
        )
        self.shape.density = self.density_3d
        self.top = (0, self.radius)
        self.bottom = (0, -self.radius)
        self.left = (-self.radius, 0)
        self.right = (self.radius, 0)

    def draw(self, surface):
        x, y = self.sim.meta.pymunk_to_pygame_point(self.body.position, surface)
        pygame.draw.circle(
            surface,
            self.color,
            (int(x), int(y)),
            self.sim.meta.pymunk_to_pygame_scale(self.radius),
        )
