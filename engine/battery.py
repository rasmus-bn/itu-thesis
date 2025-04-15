from typing import override
import pygame
from pymunk import Body
from engine.types import IBattery
from sim_math.world_meta import WorldMeta


class Battery(IBattery):
    def __init__(
        self,
        meta: WorldMeta,
        body: Body,
        capacity__wh: float,
        initial__wh: float = None,
        max_voltage__v: float = None,
        ignore_max_voltage: bool = False,
        infinite_power: bool = False,
        draw_debug: bool = False,
    ):
        super().__init__(
            meta=meta,
            body=body,
            capacity__wh=capacity__wh,
            remaining__wh=capacity__wh if initial__wh is None else initial__wh,
        )
        self._max_voltage__v = max_voltage__v
        self._ignore_max_voltage = ignore_max_voltage
        self._infinite_power = infinite_power
        self._draw_debug = draw_debug

    @override
    def get_volts(self, volts: float):
        if self._max_voltage__v:
            return min(volts, self._max_voltage__v)
        else:
            return volts

    @override
    def draw_power(self, volts: float, amps: float) -> bool:
        if self._infinite_power:
            return True
        watt_to_consume = volts * amps
        requested_power_wh = watt_to_consume / self.meta.hour_to_frames
        # print(
        #     f"Volts: {volts}, Amps: {amps}, Wh: {requested_power_wh}, remaining: {self.remaining__wh}"
        # )
        # Return false if the requested power exceeds the remaining capacity
        if requested_power_wh > self.remaining__wh:
            return False
        self.remaining__wh -= requested_power_wh
        # Prevent battery from charging beyond its capacity
        self.remaining__wh = min(self.remaining__wh, self.capacity__wh)
        return True

    @override
    def draw_debug(self, surface):
        if not self._draw_debug:
            return
        # Draw battery capacity bar
        bar_width = self.meta.pymunk_to_pygame_scale(100)
        bar_height = self.meta.pymunk_to_pygame_scale(10)
        bar_x = self.body.position.x - bar_width / 2
        bar_y = self.body.position.y + self.meta.pymunk_to_pygame_scale(20)
        # Calculate the width of the filled part based on remaining capacity
        filled_width = (self.remaining__wh / self.capacity__wh) * bar_width
        # Draw the empty part
        pygame.draw.rect(
            surface=surface,
            color=(30, 30, 30),
            rect=self.meta.pymunk_to_pygame_point(
                bar_x + filled_width, bar_y, bar_width - filled_width, bar_height
            ),
        )
        # Draw the filled part
        pygame.draw.rect(
            surface=surface,
            color=(0, 255, 0),
            rect=self.meta.pymunk_to_pygame_point(
                bar_x, bar_y, filled_width, bar_height
            ),
        )
