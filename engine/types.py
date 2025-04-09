from dataclasses import dataclass
from enum import Enum, auto
from time import time
from pymunk import Body, Vec2d
from engine.objects import IGameObject
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


@dataclass
class IBattery(IComponent):
    meta: WorldMeta
    capacity_wh: float
    remaining_wh: float
    voltage: float

    def get_volts(self, requested_volts: float) -> float:
        raise NotImplementedError("This method should be implemented in a subclass")

    def draw_power(self, volts: float, amps: float) -> float:
        raise NotImplementedError("This method should be implemented in a subclass")


@dataclass
class IMotor(IComponent):
    meta: WorldMeta
    battery: IBattery
    body: Body
    wheel_position__cm: tuple[float, float]
    wheel_radius__m: float
    wheel_speed__rad_s: float = 0.0
    torque__n_m: float = 0.0
    back_emf__v: float = 0.0

    def request_force(self, force__n: float) -> None:
        raise NotImplementedError("This method should be implemented in a subclass")

    def preupdate(self) -> None:
        pass

    def update(self) -> None:
        pass

    def postupdate(self) -> None:
        pass


# @dataclass
# class IRobotSpec:
#     battery_mass_kg: float
#     motor_mass_kg: float

#     motor_count: int
#     diameter_to_height_ratio: float

#     motor_volume_m3: float
#     battery_volume_m3: float
#     total_volume_m3: float

#     robot_height_m: float
#     robot_diameter_m: float

#     battery_capacity_wh: float

#     robot_torque_nm: float
#     motor_torque_nm: float
