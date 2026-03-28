class Timer:
    def __init__(self, duration):
        self.elapsed = 0
        self.duration = duration
        self.running = False

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def reset(self):
        self.elapsed = 0

    def update(self, dt):
        if self.running:
            self.elapsed = min(self.duration, self.elapsed + dt)

    def is_finished(self):
        return self.elapsed >= self.duration


