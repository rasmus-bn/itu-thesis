from typing import override
try:
    import pygame
except ImportError:
    pass
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
        infinite_power: bool = False,
        draw_debugging: bool = False,
        power_draw_scaler: float = 1.0,
    ):
        super().__init__(
            meta=meta,
            body=body,
            capacity__wh=capacity__wh,
            remaining__wh=capacity__wh if initial__wh is None else initial__wh,
            infinite_power=infinite_power,
            draw_debugging=draw_debugging,
            power_draw_scaler=power_draw_scaler,
        )

    @override
    def draw_power(self, volts: float, amps: float) -> bool:
        if self.infinite_power:
            return True
        watt_to_consume = volts * amps
        requested_power_wh = watt_to_consume / self.meta.hour_to_frames
        requested_power_wh *= self.power_draw_scaler
        # Return false if the requested power exceeds the remaining capacity
        if requested_power_wh > self.remaining__wh:
            return False
        self.remaining__wh -= requested_power_wh
        # Prevent battery from charging beyond its capacity
        self.remaining__wh = min(self.remaining__wh, self.capacity__wh)
        return True

    @override
    def draw_debug(self, surface):
        if not self.draw_debugging:
            return
        # Draw battery vertical capacity bar
        bar_width = 10
        bar_height = 30
        bar_position = self.meta.pymunk_to_pygame_point(self.body.position, surface=surface)
        bar_position = (bar_position[0] - self.meta.pymunk_to_pygame_scale(200) - bar_width, bar_position[1] - bar_height / 2)

        # Draw the background part
        pygame.draw.rect(
            surface=surface,
            color=(255, 0, 0),
            rect=pygame.Rect(
                bar_position[0],
                bar_position[1],
                bar_width,
                bar_height,
            ),
        )
        # Draw the filled part
        filled_height = int(bar_height * (self.remaining__wh / self.capacity__wh))
        pygame.draw.rect(
            surface=surface,
            color=(0, 255, 0),
            rect=pygame.Rect(
                bar_position[0],
                bar_position[1] + (bar_height - filled_height),
                bar_width,
                filled_height,
            ),
        )
        # Write the remaining percentage
        font = pygame.font.Font(None, 15)
        remaining_percentage = (self.remaining__wh / self.capacity__wh) * 100
        text = font.render(f"{remaining_percentage:.1f}%", True, (255, 255, 255))
        text_rect = text.get_rect(center=(bar_position[0] + bar_width / 2, bar_position[1] - 10))
        surface.blit(text, text_rect)