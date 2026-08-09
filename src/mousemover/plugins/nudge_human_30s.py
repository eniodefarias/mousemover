import random
from mousemover.core.monitors import point_on_any_monitor


class MovementPlugin:
    name = "nudge_humano_30s"
    idle_seconds = 30.0

    def __init__(self):
        self.last_nudge = 0.0

    def get_next_points(self, ctx):
        reference = max(ctx.last_user_activity, self.last_nudge)
        if (ctx.now - reference) < self.idle_seconds:
            return []

        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            x, y = ctx.current_x + dx, ctx.current_y + dy
            if point_on_any_monitor(x, y):
                self.last_nudge = ctx.now
                return [(x, y)]

        return []
