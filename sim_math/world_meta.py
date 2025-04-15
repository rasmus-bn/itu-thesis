from sim_math.units import AngularSpeed, Speed, TimeSpan


class WorldMeta:
    def __init__(
        self,
        screen_width: int = 640,
        screen_height: int = 480,
        background_color: tuple[int, int, int] = (20, 20, 20),
        camera_scale: float = 0.25,
        fps: int = 60,
    ):
        # Visualization
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.background_color = background_color
        self.camera_scale = camera_scale

        # Camera
        self.camera_offset = [0, 0]
        self.base_offset = [screen_width / 2, screen_height / 2]
        self.CAMERA_MOVE_SPEED = 10.0
        self.CAMERA_ZOOM_SPEED = 1.01

        # Time
        self.fps = fps

        # Initilize units
        TimeSpan.initialize(fps=fps)
        Speed.initialize(fps=fps)
        AngularSpeed.initialize(fps=fps)

        # Derived units
        self.km_to_cm = 100_000
        self.m_to_cm = 100
        self.hour_to_seconds = 3_600
        self.hour_to_frames = self.fps * self.hour_to_seconds
        self.cm_frames_to_km_h = self.fps * (self.hour_to_seconds / self.km_to_cm)
        self.newton_to_g_cm_2 = 100_000

    def pymunk_to_pygame_point(self, point: tuple, surface):
        return (
            point[0] - self.camera_offset[0]
        ) * self.camera_scale + self.base_offset[0], (
            point[1] - self.camera_offset[1]
        ) * -1 * self.camera_scale + self.base_offset[1]

    def pymunk_to_pygame_scale(self, value: float):
        return int(value * self.camera_scale)

    def convert_speed(self, cm_per_frame: float) -> float:
        """Calculate the speed in km/h from cm/frame"""
        return abs(cm_per_frame) * self.cm_frames_to_km_h


if __name__ == "__main__":
    wm = WorldMeta()
    print(f"Camera offset: {wm.camera_offset}")
    print(f"km to cm: {wm.km_to_cm}")
    print(f"hour to seconds: {wm.hour_to_seconds}")
    print(f"cm_frames_to_km_h: {wm.cm_frames_to_km_h}")
    print(f"Speed: {wm.convert_speed(37)}")
