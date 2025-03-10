from pygame import Surface


def pymunk_to_pygame_point(point: tuple, surface: Surface):
    return int(point[0]), surface.get_height() - int(point[1])