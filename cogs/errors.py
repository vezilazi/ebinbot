import discord
from discord.ext import commands

def ignorable(error):
    ignored_errors = [
        commands.CommandNotFound, commands.NotOwner,
        discord.ConnectionClosed, commands.CheckFailure
    ]

    for ignored in ignored_errors:
        if isinstance(error, ignored):
            return True

class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if ignorable(error):
            return
        
        cause = error.__cause__
        embed = discord.Embed()

        if isinstance(cause, discord.Forbidden):
            embed.description = f"```diff\n- I don't have permission to do that, either due to missing permissions or hierarchy.\n```"
        else:
            embed.description = f"```diff\n- {error.__class__.__name__}: {error}\n```"

        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(Errors(bot))