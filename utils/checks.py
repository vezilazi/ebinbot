class Checks:
    def __init__(self, bot):
        self.bot = bot

    def is_manager(self, ctx) -> bool:
        return ctx.author.id in self.bot.config["managers"]