import random


class MovementPlugin:
    name = "basic"

    def _jitter(self, ctx):
        amount = random.randint(ctx.jitter_min, ctx.jitter_max)
        return random.choice((-amount, amount))

    def get_next_points(self, ctx):
        return [
            (ctx.center_x + self._jitter(ctx), ctx.center_y + self._jitter(ctx)),
            (ctx.center_x - 200 + self._jitter(ctx), ctx.center_y + self._jitter(ctx)),
            (ctx.center_x + self._jitter(ctx), ctx.center_y + self._jitter(ctx)),
        ]
