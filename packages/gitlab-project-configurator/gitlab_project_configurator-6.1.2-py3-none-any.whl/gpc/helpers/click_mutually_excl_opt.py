# Third Party Libraries
from click import Option
from click import UsageError


# Gist from: https://gist.github.com/jacobtolar/fb80d5552a9a9dfc32b12a829fa21c0c


class MutuallyExclusiveOption(Option):
    def __init__(self, *args, **kwargs):
        self.mutually_exclusive = set(kwargs.pop("mutually_exclusive", []))
        super().__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        if self.mutually_exclusive.intersection(opts) and self.name in opts:
            raise UsageError(
                f"Illegal usage: `{self.name}` is mutually exclusive with "
                f"arguments `{', '.join(self.mutually_exclusive)}`."
            )

        return super().handle_parse_result(ctx, opts, args)
