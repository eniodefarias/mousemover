import random
from mousemover.core.monitors import point_on_any_monitor


class MovementPlugin:
    name = "nudge_inteligente"

    def get_next_points(self, ctx):
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            x, y = ctx.current_x + dx, ctx.current_y + dy
            if point_on_any_monitor(x, y):
                return [(x, y)]
        return []
