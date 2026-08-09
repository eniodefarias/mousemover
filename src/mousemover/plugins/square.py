import random


class MovementPlugin:
    name = "square"

    def get_next_points(self, ctx):
        size = 200
        raw = [
            (ctx.center_x - size, ctx.center_y - size),
            (ctx.center_x + size, ctx.center_y - size),
            (ctx.center_x + size, ctx.center_y + size),
            (ctx.center_x - size, ctx.center_y + size),
            (ctx.center_x - size, ctx.center_y - size),
        ]
        return [
            (
                x + random.randint(-ctx.jitter_max, ctx.jitter_max),
                y + random.randint(-ctx.jitter_max, ctx.jitter_max),
            )
            for x, y in raw
        ]
