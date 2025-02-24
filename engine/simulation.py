from dataclasses import dataclass
import pygame
import pymunk

from engine.objects import IGameObject


@dataclass
class SimulationProps:
    world_scale: int = 10
    fps: int = 60
    enable_display: bool = True
    enable_realtime: bool = True
    pixels_x: int = 640
    pixels_y: int = 480


class SimulationBase(SimulationProps):
    def __init__(self, props: SimulationProps):
        super().__init__(**props.__dict__)
        self._game_objects: IGameObject = []

        # Physics
        self.delta_time = 1 / self.fps
        self.delta_time_alert = self.delta_time * 1.2
        self.space = pymunk.Space()
        self.space.gravity = (0, -100)

        # Visualization
        self._display = None
        self._clock = None
        if self.enable_display:
            pygame.init()
            self._display = pygame.display.set_mode((self.pixels_x, self.pixels_y))
            self._clock = pygame.time.Clock()

    def _quit(self):
        # Visualization
        if self.enable_display:
            pygame.quit()

    def run(self):
        last_time = pygame.time.get_ticks()
        while True:
            actual_delta_time = (pygame.time.get_ticks() - last_time) / 1000
            last_time = pygame.time.get_ticks()
            if actual_delta_time > self.delta_time_alert:
                print(
                    f"Warning: Frame took {actual_delta_time} seconds, expected {self.delta_time}"
                )

            # Logic
            self._update_logic()

            # Physics
            self.space.step(self.delta_time)

            # Visualization
            if self.enable_display:
                # Quit on exit
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self._quit()
                        return
                # Update visuals
                self._update_visuals()
                # Update the screen
                pygame.display.update()
                # Sleep to maintain FPS
                if self.enable_realtime:
                    self._clock.tick(self.fps)

    def _update_logic(self):
        self.update()
        for obj in self._game_objects:
            obj.update()

    def _update_visuals(self):
        if self.enable_display:
            self._display.fill((0, 0, 0))
            for obj in self._game_objects:
                obj.draw(self._display)

    def update(self):
        pass

    def add_game_object(self, obj: IGameObject):
        self._game_objects.append(obj)
        self.space.add(obj.body, obj.shape)


if __name__ == "__main__":
    sim = SimulationBase(SimulationProps())
    sim.run()
