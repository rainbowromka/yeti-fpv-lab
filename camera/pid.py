class PID:
    def __init__(self, kp=1.0, ki=0.0, kd=0.0, min_output = -1.0, max_output=1.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.min_output = min_output
        self.max_output = max_output

        self.prev_error = 0.0
        self.integral = 0.0

    def update(self, error, dt):
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt if dt > 0 else 0.0
        self.prev_error = error

        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        return max(self.min_output, min(self.max_output, output))

    def reset(self):
        self.prev_error = 0.0
        self.integral = 0.0