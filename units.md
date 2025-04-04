Positions in the coordinate system is:
`centimetres (cm)`

Units of distances are:
`centimetres (cm)`

Units of mass is:
`grams (g)`

Unit of speed is:
`km/h`

Unit of force is (linear):
`Newton (N)`

Unit of torque is (rotational force):
`Newton-meters (Nm)`

Unit of battery capacity (energy):
`Watt-hours (Wh)`

## Force

The force unit is defined by the chosen distance unit for pymunk. We have chosen cm as distance units, which means that our weight unit is grams.

```
1 Newton (N) = 1 kg·m/s²
--------
1kg = 1000g (pymonk weight unit)
1m = 100cm (pymonk distance unit)
--------
1N = 1000g * 100cm / s² = 100,000 g·cm/s²
```

The force units are not dependant on the SIM FPS.

## Simulating the mass of 3D objects in the 2D game engine

We can properly calculate the mass of a 3D object by multiplying the density with the height of the object.

Pymonk calculates mass like this
`mass = area * density`

If we assume the height of 1 the result would be the same:
`mass = area * density * 1`

However if we have a height of 3 AKA 3 layers of the above mass, then the calculation should look like this:
`mass = area * density * 3`

**The hack:**

If we multiply the density of the pymonk objects with the "virtual" height then this would adjust the calculated mass accordingly.
