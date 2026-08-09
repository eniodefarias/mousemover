import random


class MovementPlugin:
    name = "random_walk"

    def get_next_points(self, ctx):
        return [
            (
                ctx.center_x + random.randint(-250, 250),
                ctx.center_y + random.randint(-150, 150),
            )
            for _ in range(5)
        ]
