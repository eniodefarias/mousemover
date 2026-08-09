import random


class MovementPlugin:
    name = "one_pixel_nudge"

    def get_next_points(self, ctx):
        dx, dy = random.choice(((0, -1), (0, 1), (-1, 0), (1, 0)))
        return [(ctx.current_x + dx, ctx.current_y + dy)]
