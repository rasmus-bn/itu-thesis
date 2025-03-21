from dataclasses import dataclass
from enum import Enum, auto
from time import time
from pymunk import Vec2d
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
    position: Vec2d
    neighbors: {}
    is_homebase: bool

    def to_message(self):
        """Convert to a str message"""
        return f"{self.id},{self.position.x},{self.position.y},{self.is_homebase}"

    @classmethod
    def from_message(cls, message: str):
        """Create an instance from a str message"""
        id, x, y, is_homebase = message.split(",")
        return cls(int(id), Vec2d(float(x), float(y)), {}, is_homebase == "True")


class DebugMessage:
    def __init__(self, message: any):
        self.timestamp = time()
        self.message: any = message


class Direction(Enum):
    NORTH = auto()
    NORTH_EAST = auto()
    EAST = auto()
    SOUTH_EAST = auto()
    SOUTH = auto()
    SOUTH_WEST = auto()
    WEST = auto()
    NORTH_WEST = auto()
