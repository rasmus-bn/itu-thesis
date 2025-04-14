import math
from typing import Self

from sim_math.units_base import UnitBase, UnitConverter


class Distance(UnitBase):
    """Class to convert between different units of distance. The base unit is in cm."""

    CM: UnitConverter = UnitConverter(value_in_base_unit=1, name="cm")
    M: UnitConverter = UnitConverter(value_in_base_unit=1 / 100, name="m")
    KM: UnitConverter = UnitConverter(value_in_base_unit=1 / 100_000, name="km")

    @classmethod
    def in_cm(cls, value: float) -> Self:
        return cls._in_unit(value, cls.CM)

    @classmethod
    def in_m(cls, value: float) -> Self:
        return cls._in_unit(value, cls.M)

    @classmethod
    def in_km(cls, value: float) -> Self:
        return cls._in_unit(value, cls.KM)

    @property
    def cm(self) -> float:
        return self._convert_to(Distance.CM)

    @property
    def m(self) -> float:
        return self._convert_to(Distance.M)

    @property
    def km(self) -> float:
        return self._convert_to(Distance.KM)


class TimeSpan(UnitBase):
    """Class to convert between different units of time. The base unit is in frames (requires initilization)."""

    SECOND: UnitConverter = UnitConverter(value_in_base_unit=None, name="s")
    MINUTE: UnitConverter = UnitConverter(value_in_base_unit=None, name="min")
    HOUR: UnitConverter = UnitConverter(value_in_base_unit=None, name="h")

    @classmethod
    def initialize(cls, fps: int) -> None:
        cls.SECOND.value_in_base_unit = 1 / fps
        cls.MINUTE.value_in_base_unit = 1 / 60 / fps
        cls.HOUR.value_in_base_unit = 1 / 3600 / fps

    @classmethod
    def in_second(cls, value: float) -> Self:
        return cls._in_unit(value, cls.SECOND)

    @classmethod
    def in_minute(cls, value: float) -> Self:
        return cls._in_unit(value, cls.MINUTE)

    @classmethod
    def in_hour(cls, value: float) -> Self:
        return cls._in_unit(value, cls.HOUR)

    @property
    def second(self) -> float:
        return self._convert_to(TimeSpan.SECOND)

    @property
    def minute(self) -> float:
        return self._convert_to(TimeSpan.MINUTE)

    @property
    def hour(self) -> float:
        return self._convert_to(TimeSpan.HOUR)


class Volume(UnitBase):
    """Class to convert between different units of volume. The base unit is in cm³."""

    CM3: UnitConverter = UnitConverter(value_in_base_unit=1, name="cm³")
    LITRE: UnitConverter = UnitConverter(value_in_base_unit=1 / 1000, name="l")
    M3: UnitConverter = UnitConverter(value_in_base_unit=1 / 1_000_000, name="m³")

    @classmethod
    def in_cm3(cls, value: float) -> Self:
        return cls._in_unit(value, cls.CM3)

    @classmethod
    def in_litre(cls, value: float) -> Self:
        return cls._in_unit(value, cls.LITRE)

    @classmethod
    def in_m3(cls, value: float) -> Self:
        return cls._in_unit(value, cls.M3)

    @property
    def cm3(self) -> float:
        return self._convert_to(Volume.CM3)

    @property
    def litre(self) -> float:
        return self._convert_to(Volume.LITRE)

    @property
    def m3(self) -> float:
        return self._convert_to(Volume.M3)


class Mass(UnitBase):
    """Class to convert between different units of mass. The base unit is in grams."""

    G: UnitConverter = UnitConverter(value_in_base_unit=1, name="g")
    KG: UnitConverter = UnitConverter(value_in_base_unit=1 / 1000, name="kg")

    @classmethod
    def in_g(cls, value: float) -> Self:
        return cls._in_unit(value, cls.G)

    @classmethod
    def in_kg(cls, value: float) -> Self:
        return cls._in_unit(value, cls.KG)

    @property
    def g(self) -> float:
        return self._convert_to(Mass.G)

    @property
    def kg(self) -> float:
        return self._convert_to(Mass.KG)


class Density2d(UnitBase):
    """Class to convert between different units of 2D density. The base unit is in g/cm².
    Be aware that 1 g/cm² > 1 kg/m²."""

    G_CM2: UnitConverter = UnitConverter(value_in_base_unit=1, name="g/cm²")
    KG_M2: UnitConverter = UnitConverter(value_in_base_unit=10, name="kg/m²")

    @classmethod
    def in_g_cm2(cls, value: float) -> Self:
        return cls._in_unit(value, cls.G_CM2)

    @classmethod
    def in_kg_m2(cls, value: float) -> Self:
        return cls._in_unit(value, cls.KG_M2)

    @property
    def g_cm2(self) -> float:
        return self._convert_to(Density2d.G_CM2)

    @property
    def kg_m2(self) -> float:
        return self._convert_to(Density2d.KG_M2)

    def to_3d(self, height: Distance) -> "Density3d":
        """Convert 2D density to 3D density assuming that the mass stays the same."""
        return Density3d.in_g_cm3(self.g_cm2 / height.cm)


class Density3d(UnitBase):
    """Class to convert between different units of 3D density. The base unit is in g/cm³.
    Be aware that 1 g/cm³ > 1 kg/m³."""

    G_CM3: UnitConverter = UnitConverter(value_in_base_unit=1, name="g/cm³")
    KG_M3: UnitConverter = UnitConverter(value_in_base_unit=1000, name="kg/m³")

    @classmethod
    def in_g_cm3(cls, value: float) -> Self:
        return cls._in_unit(value, cls.G_CM3)

    @classmethod
    def in_kg_m3(cls, value: float) -> Self:
        return cls._in_unit(value, cls.KG_M3)

    @property
    def g_cm3(self) -> float:
        return self._convert_to(Density3d.G_CM3)

    @property
    def kg_m3(self) -> float:
        return self._convert_to(Density3d.KG_M3)

    def to_2d(self, height: Distance) -> Density2d:
        """Convert 3D density to 2D density assuming that the mass stays the same."""
        return Density2d.in_g_cm2(self.g_cm3 * height.cm)


class Force(UnitBase):
    """Class to convert between different units of force. The base unit is in newtons."""

    DYNE: UnitConverter = UnitConverter(value_in_base_unit=1, name="dyne")
    N: UnitConverter = UnitConverter(value_in_base_unit=1 / 100_000, name="N")

    @classmethod
    def in_dyne(cls, value: float) -> Self:
        return cls._in_unit(value, cls.DYNE)

    @classmethod
    def in_n(cls, value: float) -> Self:
        return cls._in_unit(value, cls.N)

    @property
    def dyne(self) -> float:
        return self._convert_to(Force.DYNE)

    @property
    def n(self) -> float:
        return self._convert_to(Force.N)

    def to_torque_at(self, radius: Distance) -> "Torque":
        """Convert force to torque.
            T = F * r
        where:
            T = torque (Nm)
            F = force (N)
            r = radius (m)
        """
        return Torque.in_base_unit(self.base_unit * radius.base_unit)


class Torque(UnitBase):
    """Class to convert between different units of torque. The base unit is in newton meters."""

    DYNE_CM: UnitConverter = UnitConverter(value_in_base_unit=1, name="dyne cm")
    NM: UnitConverter = UnitConverter(value_in_base_unit=1 / 10_000_000, name="Nm")

    @classmethod
    def in_dyne_cm(cls, value: float) -> Self:
        return cls._in_unit(value, cls.DYNE_CM)

    @classmethod
    def in_nm(cls, value: float) -> Self:
        return cls._in_unit(value, cls.NM)

    @property
    def dyne_cm(self) -> float:
        return self._convert_to(Torque.DYNE_CM)

    @property
    def nm(self) -> float:
        return self._convert_to(Torque.NM)

    def to_force_at(self, radius: Distance) -> Force:
        """Convert torque to force.
            F = T / r
        where:
            F = force (N)
            T = torque (Nm)
            r = radius (m)
        """
        return Force.in_base_unit(self / radius)


class Speed(UnitBase):
    """Class to convert between different units of speed. The base unit is in cm/frames (requires initilization)."""

    CM_S: UnitConverter = UnitConverter(value_in_base_unit=None, name="cm/s")
    KM_H: UnitConverter = UnitConverter(value_in_base_unit=None, name="km/h")

    @classmethod
    def initialize(cls, fps: int) -> None:
        Speed.CM_S.value_in_base_unit = 1 * fps
        Speed.KM_H.value_in_base_unit = 0.036 * fps

    @classmethod
    def in_cm_s(cls, value: float) -> Self:
        return cls._in_unit(value, cls.CM_S)

    @classmethod
    def in_km_h(cls, value: float) -> Self:
        return cls._in_unit(value, cls.KM_H)

    @property
    def cm_s(self) -> float:
        return self._convert_to(Speed.CM_S)

    @property
    def km_h(self) -> float:
        return self._convert_to(Speed.KM_H)


class AngularSpeed(UnitBase):
    """Class to convert between different units of rotational speed. The base unit is in rad/s."""

    RAD_S: UnitConverter = UnitConverter(value_in_base_unit=None, name="rad/s")
    RPM: UnitConverter = UnitConverter(value_in_base_unit=None, name="rpm")

    @classmethod
    def initialize(cls, fps: int) -> None:
        AngularSpeed.RAD_S.value_in_base_unit = 1 * fps
        # 1 rpm = (rad/s) * 60 / 2pi
        AngularSpeed.RPM.value_in_base_unit = (1 * fps) * (60 / (2 * math.pi))

    @classmethod
    def in_rad_s(cls, value: float) -> Self:
        return cls._in_unit(value, cls.RAD_S)

    @classmethod
    def in_rpm(cls, value: float) -> Self:
        return cls._in_unit(value, cls.RPM)

    @property
    def rad_s(self) -> float:
        return self._convert_to(AngularSpeed.RAD_S)

    @property
    def rpm(self) -> float:
        return self._convert_to(AngularSpeed.RPM)
