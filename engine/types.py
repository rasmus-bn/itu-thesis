from dataclasses import dataclass


@dataclass
class ILightDetection:
    distance: float
    angle: float
