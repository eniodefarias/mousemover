import random


class MovementPlugin:
    name = "erosion"

    def get_next_points(self, ctx):
        points = []
        x, y = ctx.center_x, ctx.center_y
        for _ in range(15):
            x += random.randint(-120, 120)
            y += random.randint(-80, 80)
            points.append((x, y))
        return points
