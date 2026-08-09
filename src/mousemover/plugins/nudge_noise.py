import random
from mousemover.core.monitors import point_on_any_monitor


class MovementPlugin:
    name = "nudge_noise_1px"

    def __init__(self):
        self.noise_x = 0.0
        self.noise_y = 0.0

    def get_next_points(self, ctx):
        self.noise_x = max(-1.0, min(1.0, self.noise_x + random.uniform(-0.35, 0.35)))
        self.noise_y = max(-1.0, min(1.0, self.noise_y + random.uniform(-0.35, 0.35)))

        dx = 1 if self.noise_x > 0.25 else -1 if self.noise_x < -0.25 else 0
        dy = 1 if self.noise_y > 0.25 else -1 if self.noise_y < -0.25 else 0

        if dx == 0 and dy == 0:
            if abs(self.noise_x) >= abs(self.noise_y):
                dx = 1 if self.noise_x >= 0 else -1
            else:
                dy = 1 if self.noise_y >= 0 else -1

        x, y = ctx.current_x + dx, ctx.current_y + dy
        if point_on_any_monitor(x, y):
            return [(x, y)]

        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            x, y = ctx.current_x + dx, ctx.current_y + dy
            if point_on_any_monitor(x, y):
                return [(x, y)]
        return []
