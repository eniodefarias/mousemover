import math
import random


class MovementPlugin:
    name = "circle"

    def get_next_points(self, ctx):
        points = []
        radius = 150
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            jx = random.randint(-ctx.jitter_max, ctx.jitter_max)
            jy = random.randint(-ctx.jitter_max, ctx.jitter_max)
            points.append((
                ctx.center_x + int(radius * math.cos(rad)) + jx,
                ctx.center_y + int(radius * math.sin(rad)) + jy,
            ))
        return points
