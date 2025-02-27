from engine.objects import Box
from engine.simulation import SimulationBase


size_x = 2500
size_y = 1500


sim = SimulationBase(
    pixels_x=size_x,
    pixels_y=size_y,
    enable_realtime=False,
    enable_display=False,
)


def run():
    box = Box(x=0, y=0, width=100, length=100, color=(255, 0, 0), density=100)
    sim.add_game_object(box)
    print(box.shape.mass)


run()
