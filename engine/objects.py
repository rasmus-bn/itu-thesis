from dataclasses import dataclass
from pygame import Surface
import pygame
import pymunk

from engine.helpers import pymunk_to_pygame_point




class IGameObject:
    def __init__(self, body: pymunk.Body, shape: pymunk.Shape):
        self.body = body
        self.shape = shape

    @property
    def has_update(self):
        return getattr(self.__class__, "update") is not getattr(IGameObject, "update")

    def update(self):
        pass

    def draw(self, surface: Surface):
        raise NotImplementedError()


@dataclass
class Box(IGameObject):
    x: int = 0
    y: int = 0
    width: int = 10
    height: int = 10
    color: tuple = (255, 255, 255)
    density: int = 1

    def __post_init__(self):
        self.body = pymunk.Body()
        self.body.position = (self.x, self.y)
        self.shape = pymunk.Poly.create_box(self.body, (self.width, self.height))
        self.shape.density = self.density
        IGameObject.__init__(self, self.body, self.shape)
        self.top = (0, self.height / 2)
        self.bottom = (0, self.height / 2)
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

    def __post_init__(self):
        self.body = pymunk.Body()
        self.body.position = (self.x, self.y)
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.density = self.density
        IGameObject.__init__(self, self.body, self.shape)

    def draw(self, surface):
        x, y = pymunk_to_pygame_point(self.body.position, surface)
        pygame.draw.circle(
            surface,
            self.color,
            (int(x), int(y)),
            int(self.radius),
        )
