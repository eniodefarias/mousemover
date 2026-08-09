import random


class MovementPlugin:
    name = "zigzag"

    def get_next_points(self, ctx):
        result = []
        for i in range(6):
            offset = (-1) ** i * 200
            result.append((
                ctx.center_x + offset + random.randint(-ctx.jitter_max, ctx.jitter_max),
                ctx.center_y + i * 20 + random.randint(-ctx.jitter_max, ctx.jitter_max),
            ))
        return result
