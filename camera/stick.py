class Stick:
    def __init__(self, speed, min_value=0.0, max_value=1.0, default = 0.0):
        self.value = default
        self.target = default
        self.default = default
        self.speed = speed
        self.min_value = min_value
        self.max_value = max_value

    def set_target(self, amount):
        self.target = max(self.min_value, min(self.max_value, self.target + amount))

    def update(self, dt):
        if self.target > self.value:
            self.value = min(self.target, self.value + self.speed * dt)
        elif self.target < self.value:
            self.value = max(self.target, self.value - self.speed * dt)

    def reset(self):
        self.target = self.default
        # self.value = self.min_value