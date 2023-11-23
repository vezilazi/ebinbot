import discord
from discord.ext import flags, commands

class Embed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @flags.add_flag("--title", default=None)
    @flags.add_flag("--description", default=None)
    @flags.add_flag("--footer", default=None)
    @flags.add_flag("--image", default=None)
    @flags.add_flag("--url", default=None)
    @flags.add_flag("--thumbnail", default=None)
    @flags.add_flag("--color", type=discord.Colour, default=0)
    @flags.command(name="embed", aliases=["emb"])
    @commands.has_permissions(manage_messages=True)
    async def create_embed(self, ctx, **flags):
        embed = discord.Embed(**flags)

        if ftr:=flags["footer"]:
            embed.set_footer(text=ftr)
        if img:=flags["image"]:
            embed.set_image(url=img)
        if not flags["color"]:
            embed.color = discord.Colour.random()

        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Embed(bot))