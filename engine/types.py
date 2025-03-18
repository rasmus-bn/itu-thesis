from dataclasses import dataclass
from pymunk import vec2d
from engine.objects import IGameObject


@dataclass
class ILightData:
    distance: float
    angle: float


@dataclass
class ILidarData:
    angle: int
    distance: float
    gameobject: IGameObject | None


@dataclass
class IWaypointData:
    id: int
    position: vec2d
    neighbors: {}
    is_homebase: bool
