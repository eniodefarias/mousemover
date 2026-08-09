import random


class MovementPlugin:
    name = "fractal_walk"

    def get_next_points(self, ctx):
        points = []
        x, y = ctx.center_x, ctx.center_y
        for _ in range(30):
            x += random.randint(-200, 200) + int(random.gauss(0, 50))
            y += random.randint(-200, 200) + int(random.gauss(0, 50))
            points.append((x, y))
        return points
