from dataclasses import dataclass
from pygame import Surface
import pygame
import pymunk

from engine.helpers import pymunk_to_pygame_point


@dataclass
class LightDetection:
    distance: float
    angle: float


print(LightDetection.angle)


# class LightSensor:
#     def __init__(self, game_object):
#         self.game_object = game_object
#         self._detections: list[LightDetection] = []

#     def on_light_discovered(self, detection: LightDetection):
#         self._detections.append(detection)

#     def clear_detections(self):
#         self._detections.clear()

#     def get_detections(self):
#         return self._detections.copy()


# class LightEmitter:
#     def __init__(
#         self, body: pymunk.Body, shape_filter: pymunk.ShapeFilter, range: float
#     ):
#         self._body = body
#         self._shape_filter = shape_filter
#         self._range = range
#         self._on = False

#     def update(self):
#         if self._on:
#             self._emit_light()

#     def _emit_light(self):
#         space = self._body.space
#         self._body.shapes
#         # Finds all shapes within a range of the body's position
#         shapes = space.point_query(self._body.position, self._range, self._shape_filter)
#         for shape in shapes:
#             obj = shape.shape.body.gameobject
#             if isinstance(obj, LightSensor):
#                 distance = obj.game_object.body.position.get_distance(
#                     self._body.position
#                 )
#                 angle = obj.game_object.body.position.get_angle(self._body.position)
#                 # Add the emitter to the sensor's detections
#                 obj.on_light_discovered(LightDetection(distance, angle))

#     def draw(self, surface: Surface):
#         if self._on:
#             x, y = pymunk_to_pygame_point(self._body.position, surface)
#             pygame.draw.circle(surface, (255, 255, 0), (x, y), self._range, 1)
