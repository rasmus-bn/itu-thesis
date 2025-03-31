class PID:
    def __init__(self, Kp=1.0, Ki=0.0, Kd=0.0):
        self.Kp = Kp  # Proportional gain
        self.Ki = Ki  # Integral gain
        self.Kd = Kd  # Derivative gain
        self.prev_error = 0
        self.integral = 0

    def compute(self, error):
        dt = 1/60

        self.integral += error * dt  # Accumulate integral
        derivative = (error - self.prev_error) / dt  # Compute derivative
        self.prev_error = error

        return self.Kp * error + self.Ki * self.integral + self.Kd * derivative