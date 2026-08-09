import math
import random


class MovementPlugin:
    name = "spiral"

    def get_next_points(self, ctx):
        result = []
        radius = 20
        for i in range(20):
            rad = math.radians(i * 18)
            result.append((
                ctx.center_x + int(radius * math.cos(rad)) + random.randint(-ctx.jitter_max, ctx.jitter_max),
                ctx.center_y + int(radius * math.sin(rad)) + random.randint(-ctx.jitter_max, ctx.jitter_max),
            ))
            radius += 10
        return result
