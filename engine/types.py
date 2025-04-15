from dataclasses import dataclass
from enum import Enum, auto
from time import time
from pygame import Surface
from pymunk import Body, Vec2d
from engine.objects import IGameObject
from sim_math.units import Density2d, Density3d, Distance, Force, Mass, Torque, Volume
from sim_math.world_meta import WorldMeta


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


class IComponent:
    def preupdate(self) -> None:
        pass

    def update(self) -> None:
        pass

    def postupdate(self) -> None:
        pass

    def draw(self, surface: Surface) -> None:
        pass

    def draw_debug(self, surface: Surface) -> None:
        pass


@dataclass
class IBattery(IComponent):
    meta: WorldMeta
    body: Body
    capacity__wh: float
    remaining__wh: float = 0

    def get_volts(self, requested_volts: float) -> float:
        raise NotImplementedError("This method should be implemented in a subclass")

    def draw_power(self, volts: float, amps: float) -> float:
        raise NotImplementedError("This method should be implemented in a subclass")


@dataclass
class IMotor(IComponent):
    meta: WorldMeta
    battery: IBattery
    body: Body
    wheel_position: tuple[float, float]
    wheel_radius: Distance

    def request_force(self, force: Force) -> None:
        raise NotImplementedError("This method should be implemented in a subclass")

    def request_force_scaled(self, force_scaler: float) -> None:
        raise NotImplementedError("This method should be implemented in a subclass")


@dataclass
class IRobotSpec:
    # Robot dimensions
    robot_diameter: Distance
    robot_height: Distance
    wheel_radius: Distance

    # Physics
    robot_density_2d: Density2d

    # Robot performance
    battery_capacity__wh: float
    max_motor_torque: Torque
    max_motor_voltage: float

    # Meta data
    robot_volume: Volume
    mass: Mass
    robot_density_3d: Density3d
