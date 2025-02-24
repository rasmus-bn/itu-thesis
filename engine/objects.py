from dataclasses import dataclass
from pygame import Surface
import pygame
import pymunk


def pymunk_to_pygame_point(point: tuple, pixel_height):
    return int(point[0]), pixel_height - int(point[1])


class IGameObject:
    def __init__(self, bode: pymunk.Body, shape: pymunk.Shape):
        self.body = bode
        self.shape = shape

    def update(self):
        pass

    def draw(self, surface: Surface):
        raise NotImplementedError()


@dataclass
class BoxProps:
    x: int = 0
    y: int = 0
    width: int = 10
    height: int = 10
    color: tuple = (255, 255, 255)
    density: int = 1


class Box(IGameObject, BoxProps):
    def __init__(self, props: BoxProps):
        BoxProps.__init__(self, **props.__dict__)
        self.body = pymunk.Body()
        self.body.position = (self.x, self.y)
        # self.body = pymunk.Body(self.mass, pymunk.moment_for_box(self.mass, (self.width, self.height)))
        self.shape = pymunk.Poly.create_box(self.body, (self.width, self.height))
        self.shape.density = self.density
        IGameObject.__init__(self, self.body, self.shape)

    def draw(self, surface):
        x, y = pymunk_to_pygame_point(self.body.position, surface.get_height())
        pygame.draw.rect(
            surface,
            self.color,
            (
                int(x - self.width / 2),
                int(y - self.height / 2),
                int(self.width),
                int(self.height),
            ),
        )


@dataclass
class CircleProps:
    x: int = 0
    y: int = 0
    radius: int = 10
    color: tuple = (255, 255, 255)
    density: int = 1


class Circle(IGameObject, CircleProps):
    def __init__(self, props: CircleProps):
        CircleProps.__init__(self, **props.__dict__)
        self.body = pymunk.Body()
        self.body.position = (self.x, self.y)
        self.shape = pymunk.Circle(self.body, self.radius)
        self.shape.density = self.density
        IGameObject.__init__(self, self.body, self.shape)

    def draw(self, surface):
        x, y = pymunk_to_pygame_point(self.body.position, surface.get_height())
        pygame.draw.circle(
            surface,
            self.color,
            (int(x), int(y)),
            int(self.radius),
        )
