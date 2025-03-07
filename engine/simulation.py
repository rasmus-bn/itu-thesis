from dataclasses import dataclass
from time import time
import pygame
import pymunk

from engine.constraints import IConstraint
from engine.objects import IGameObject


@dataclass
class SimulationBase:
    world_scale: int = 10
    fps: int = 60
    enable_display: bool = True
    enable_realtime: bool = True
    pixels_x: int = 640
    pixels_y: int = 480
    background_color: tuple = (100, 100, 100)
    frame_count: int = 0
    start_time: float = None
    end_time: float = None
    run_time: float = None

    def __post_init__(self):
        self._game_objects: IGameObject = []
        self._logic_objects = None
        self._constraints: IConstraint = []

        # Physics
        self.delta_time = 1 / self.fps
        self.delta_time_alert = self.delta_time * 1.2
        self.space = pymunk.Space()
        # How much energy is lost over time
        self.space.damping = 0.50

        # Visualization
        self._display = None
        self._clock = None

    def _start(self):
        self._logic_objects = [go for go in self._game_objects if go.has_update]
        self.start_time = time()

        # Visualization
        if self.enable_display:
            pygame.init()
            self._display = pygame.display.set_mode((self.pixels_x, self.pixels_y))
            self._clock = pygame.time.Clock()

    def _quit(self):
        self.end_time = time()
        run_time = self.end_time - self.start_time
        expected_time = self.frame_count / self.fps
        print(f"Ran faster by a factor of {expected_time / run_time}")

        # Visualization
        if self.enable_display:
            pygame.quit()

    def run(self):
        self._start()
        last_time = pygame.time.get_ticks()
        while True:
            actual_delta_time = (pygame.time.get_ticks() - last_time) / 1000
            last_time = pygame.time.get_ticks()
            if actual_delta_time > self.delta_time_alert:
                print(
                    f"Warning: Frame took {actual_delta_time} seconds, expected {self.delta_time}"
                )
            self.frame_count += 1
            print(f"Frame {self.frame_count}")

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
        for obj in self._logic_objects:
            obj.update()
        for constraint in self._constraints:
            if not constraint.alive:
                self.space.remove(constraint.constraint)

    def _update_visuals(self):
        if self.enable_display:
            self._display.fill(self.background_color)
            # Draw all objects
            for obj in self._game_objects:
                obj.draw(self._display)
            # Draw all constraints
            for constraint in self._constraints:
                constraint.draw(self._display)

    def update(self):
        pass

    def add_game_object(self, obj: IGameObject):
        self._game_objects.append(obj)
        self.space.add(obj.body, obj.shape)

    def add_constraint(self, constraint: IConstraint):
        self._constraints.append(constraint)
        self.space.add(constraint.constraint)
        # constraint.add_to_space(self.space)


if __name__ == "__main__":
    sim = SimulationBase()
    sim.run()
