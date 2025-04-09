class Battery:
    # Assumed values
    DENSITY = 0.5  # kg/m³
    CAPACITY_TO_MASS_RATIO = 1000  # Wh/kg

    def __init__(self, mass_kg: float):
        self.mass_kg = mass_kg  # in kg
        self.battery_volume_m3 = self.mass_kg / Battery.DENSITY
        self.capacity_wh = self.mass_kg * Battery.CAPACITY_TO_MASS_RATIO
        self.remaining_wh = self.capacity_wh
        self.voltage = 100_000  # Vary based on mass?

    def get_volts(self, volts: float):
        return min(volts, self.voltage)

    def draw_power(self, volts: float, amps: float) -> bool:
        power_drawn = volts * amps
        if power_drawn > self.remaining_wh:
            return False
        self.remaining_wh -= power_drawn
        #
        self.remaining_wh = min(self.remaining_wh, self.capacity_wh)
        return True

    # def draw_power(self, volts: float, amps: float):
    #     """Calculate the power drawn from the battery in watts"""
    #     return volts * amps
