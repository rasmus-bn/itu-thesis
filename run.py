import pymunk
import random
from engine.objects import Box, BoxProps, Circle, CircleProps
from engine.simulation import SimulationBase, SimulationProps


box = Box(BoxProps(x=200, y=500, width=50, height=50, color=(255, 0, 0)))
box2 = Box(BoxProps(x=230, y=550, width=25, height=25, color=(0, 255, 0)))

size_x = 1280
size_y = 720

sim = SimulationBase(SimulationProps(pixels_x=size_x, pixels_y=size_y))
sim.add_game_object(box)
sim.add_game_object(box2)

circle = Circle(CircleProps(x=300, y=500, radius=25, color=(0, 0, 255)))
sim.add_game_object(circle)

# Create additional 5 random boxes
padding = 20
for _ in range(1000):
    x = random.randint(padding, size_x - padding)
    y = random.randint(padding, size_y - padding)
    width = random.randint(5, padding)
    height = random.randint(5, padding)
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    box = Box(BoxProps(x=x, y=y, width=width, height=height, color=color))
    sim.add_game_object(box)

seg_body = pymunk.Body(body_type=pymunk.Body.STATIC)
seg = pymunk.Segment(
    seg_body,
    (0, 0),
    (size_x, 0),
    5,
)
sim.space.add(seg_body, seg)

sim.run()
