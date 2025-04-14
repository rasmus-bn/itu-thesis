from typing import Self
from math import trunc
from math import ceil
from math import floor


class UnitConverter:
    """Class to convert between a unit and a base unit."""

    def __init__(self, value_in_base_unit: float, name: str):
        self.value_in_base_unit = value_in_base_unit
        self.name = name

    def to_unit(self, value) -> float:
        if value == 0:
            return 0
        return value * self.value_in_base_unit

    def to_base(self, value) -> float:
        if value == 0:
            return 0
        return value / self.value_in_base_unit


class UnitBase:
    """Base class for unit conversion within a specific type of measurement. For best
    performance the base unit should be the unit used in the physics engine."""

    BASE_UNIT: UnitConverter = UnitConverter(value_in_base_unit=1, name="base_unit")

    def __init__(self, base_value: float):
        self._base_value = base_value
        self._conversions = {}

    @classmethod
    def _in_unit(cls: Self, value: float, unit: UnitConverter) -> Self:
        """Create an instance of the class based on a unit and value in the given unit."""
        return cls(base_value=unit.to_base(value))

    @classmethod
    def in_base_unit(cls, value: float) -> Self:
        """Create an instance of the class based on a value in the base unit."""
        return cls._in_unit(value, cls.BASE_UNIT)

    def _convert_to(self, unit: UnitConverter) -> float:
        """Convert the base value to the specified unit."""
        if unit.name not in self._conversions:
            self._conversions[unit.name] = unit.to_unit(self._base_value)
        return self._conversions[unit.name]

    @property
    def base_unit(self) -> float:
        """Return the base value."""
        return self._base_value

    def _get_other_value(self, other, operation_name: str) -> float:
        """Get the value of the other object in the base unit."""
        if isinstance(other, UnitBase):
            return other._base_value
        elif isinstance(other, (int, float)):
            return other
        else:
            raise TypeError(f"Unsupported type for {operation_name}: {type(other)}")

    def to_str(self, unit: UnitConverter) -> str:
        """Return the value in the specified unit as a string."""
        return f"{self._convert_to(unit)} {unit.name}"

    # String Magic Methods
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._base_value})"

    def __str__(self) -> str:
        return self.__repr__()

    # Numeric magic operators
    def __trunc__(self):
        return self.__class__(trunc(self._base_value))

    def __ceil__(self):
        return self.__class__(ceil(self._base_value))

    def __floor__(self):
        return self.__class__(floor(self._base_value))

    def __round__(self, n=None):
        return self.__class__(round(self._base_value, n))

    def __invert__(self):
        return self.__class__(~int(self._base_value))

    def __abs__(self):
        return self.__class__(abs(self._base_value))

    def __neg__(self):
        return self.__class__(-self._base_value)

    def __pos__(self):
        return self.__class__(+self._base_value)

    # Arithmetic operators

    def __add__(self, other):
        return self.__class__(
            self._base_value + self._get_other_value(other, "addition")
        )

    def __sub__(self, other):
        return self.__class__(
            self._base_value - self._get_other_value(other, "subtraction")
        )

    def __mul__(self, other):
        return self.__class__(
            self._base_value * self._get_other_value(other, "multiplication")
        )

    def __floordiv__(self, other):
        return self.__class__(
            self._base_value // self._get_other_value(other, "floor division")
        )

    def __truediv__(self, other):
        return self.__class__(
            self._base_value / self._get_other_value(other, "true division")
        )

    def __mod__(self, other):
        return self.__class__(
            self._base_value % self._get_other_value(other, "modulus")
        )

    def __divmod__(self, other):
        quotient, remainder = divmod(
            self._base_value, self._get_other_value(other, "divmod")
        )
        return self.__class__(quotient), self.__class__(remainder)

    def __pow__(self, other):
        return self.__class__(self._base_value ** self._get_other_value(other, "power"))

    def __lshift__(self, other):
        return self.__class__(
            self._base_value << self._get_other_value(other, "left shift")
        )

    def __rshift__(self, other):
        return self.__class__(
            self._base_value >> self._get_other_value(other, "right shift")
        )

    def __and__(self, other):
        return self.__class__(
            self._base_value & self._get_other_value(other, "bitwise AND")
        )

    def __or__(self, other):
        return self.__class__(
            self._base_value | self._get_other_value(other, "bitwise OR")
        )

    def __xor__(self, other):
        return self.__class__(
            self._base_value ^ self._get_other_value(other, "bitwise XOR")
        )

    # Comparison magic methods

    def __eq__(self, other):
        return self._base_value == self._get_other_value(other, "equality")

    def __ne__(self, other):
        return self._base_value != self._get_other_value(other, "inequality")

    def __lt__(self, other):
        return self._base_value < self._get_other_value(other, "less than")

    def __gt__(self, other):
        return self._base_value > self._get_other_value(other, "greater than")

    def __le__(self, other):
        return self._base_value <= self._get_other_value(other, "less than or equal to")

    def __ge__(self, other):
        return self._base_value >= self._get_other_value(
            other, "greater than or equal to"
        )
