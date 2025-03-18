from dataclasses import dataclass
from time import time
import pygame
import pymunk

from engine.tether import Tether
from engine.environment import Environment
from engine.objects import IGameObject
from sim_math.world_meta import WorldMeta


@dataclass
class SimulationBase:
    fps: int = 60
    enable_display: bool = True
    enable_realtime: bool = True
    pixels_x: int = 640
    pixels_y: int = 480
    background_color: tuple = (20, 20, 20)
    frame_count: int = 0
    start_time: float = None
    end_time: float = None
    run_time: float = None
    environment: Environment = None

    def __post_init__(self):
        self._game_objects: IGameObject = []
        self._tethers: list[Tether] = []

        # Physics
        self.delta_time = 1 / self.fps
        self.delta_time_alert = self.delta_time * 1.2
        self.space = pymunk.Space()
        # How much energy is lost over time
        self.space.damping = 0.01

        # Visualization
        self._display = None
        self._clock = None

        # World meta data
        self.meta: WorldMeta = WorldMeta(
            fps=self.fps,
            screen_width=self.pixels_x,
            screen_height=self.pixels_y,
            background_color=self.background_color,
        )

    def _start(self):
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
            # print(f"Frame {self.frame_count}")

            # Physics
            self.space.step(self.delta_time)

            # Update
            self._preupdate()
            self._update()



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

            self._postupdate()

    def _preupdate(self):
        for obj in self._game_objects:
            obj.preupdate()

    def _update(self):
        for obj in self._game_objects:
            obj.update()

    def _postupdate(self):
        for obj in self._game_objects:
            obj.postupdate()

    def _update_visuals(self):
        if self.enable_display:
            self._display.fill(self.background_color)
            # Draw all objects
            for obj in self._game_objects:
                obj.draw(self._display)
            # Draw all tethers
            for tether in self._tethers:
                tether.draw(self._display)


    def add_game_object(self, obj: IGameObject):
        obj.sim = self
        self._game_objects.append(obj)
        self.space.add(obj.body, obj.shape)

    def remove_game_object(self, obj: IGameObject):
        if obj in self._game_objects:
            self._game_objects.remove(obj)
            self.space.remove(obj.body, obj.shape)

    def add_tether(self, tether: Tether):
        self._tethers.append(tether)
        self.space.add(tether.constraint)

    def remove_tether(self, tether: Tether):
        self._tethers.remove(tether)
        self.space.remove(tether.constraint)

    def set_environment(self, env: Environment):
        self.environment = env


if __name__ == "__main__":
    sim = SimulationBase()
    sim.run()
