from dataclasses import dataclass


@dataclass
class WorldMeta:
    # Visualization
    screen_width: int = 640
    screen_height: int = 480
    background_color: tuple[int] = (20, 20, 20)
    world_scale: float = 1
    world_offset: tuple[float] = (0, 0)

    # Time
    fps: int = 60

    def __post_init__(self):
        self.km_to_cm = 100_000
        self.hour_to_seconds = 3_600
        self.cm_frames_to_km_h = self.fps * (self.hour_to_seconds / self.km_to_cm)

    def convert_speed(self, cm_per_frame: float) -> float:
        """Calculate the speed in km/h from cm/frame"""
        return abs(cm_per_frame) * self.cm_frames_to_km_h


if __name__ == "__main__":
    WorldMeta()
    print(f"km to cm: {WorldMeta().km_to_cm}")
    print(f"hour to seconds: {WorldMeta().hour_to_seconds}")
    print(f"cm_frames_to_km_h: {WorldMeta().cm_frames_to_km_h}")
    print(f"Speed: {WorldMeta().convert_speed(37)}")
