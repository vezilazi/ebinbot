import discord, base64
from discord.ext import commands
import random

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.encodings = ["b16", "b32", "b64", "b85"]

    def cog_check(self, ctx):
        return not ctx.guild is None
    
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def say(self, ctx, *, message: str):
        embed = discord.Embed(description=message, colour=ctx.author.top_role.colour)
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["clr", "color"])
    async def colour(self, ctx, clr: discord.Colour = None):
        clr = clr or discord.Colour.random()
        embed = discord.Embed(title=str(clr), colour=clr, url=f"http://google.com/search/?q={str(clr).replace('#', '%23')}&tbm=isch")
        await ctx.send(embed=embed)

    @commands.command(aliases=["roll"])
    async def dice(self, ctx, _type: str):
        if _type.count("d") != 1:
            return await ctx.reply(
                "The type of an amount of dice must be in the format of `x`d`y`" \
                "where `x` is the amount of dice and `y` is the amount of sides." \
                "For example, `1d6` would roll a single 6-sided die."
            )
        
        if len((dice:=tuple(_type.split("d")))) != 2:
            return await ctx.reply(
                "The type of an amount of dice must be in the format of `x`d`y`" \
                "where `x` is the amount of dice and `y` is the amount of sides." \
                "For example, `1d6` would roll a single 6-sided die."
            )
        
        try:
            amount, sides = (int(i) for i in dice)
        except:
            return await ctx.reply("Both the amount and sides of the dice must be integers.")
        
        if not amount >= 1:
            return await ctx.reply("The amount of dice must be greater than or equal to 1.")
        elif amount > 20:
            return await ctx.reply("The amount of dice must be less than or equal to 20.")
        
        if not sides >= 4:
            return await ctx.reply("The amount of sides must be greater than or equal to 4.")
        elif sides > 100:
            return await ctx.reply("The amount of sides must be less than or equal to 20.")
        
        rolled_score = sum(random.uniform(1, sides) for i in range(amount))
        embed = discord.Embed(title=f"Rolled {_type} :game_die:", colour=discord.Colour.random())
        embed.description = f"Rolled {amount}d{sides} and got **{rolled_score}**"
        await ctx.reply(embed=embed)

    @commands.command(name="encode", aliases=["enc"])
    async def encoding_to_str(self, ctx, encoding: str, *, _input: str):
        output = self.enc_or_dec("decode", encoding, _input)
        embed = discord.Embed(title=f"Decoded from {encoding} :lock:")
        embed.description = f"```\n{output}\n```"
        await ctx.reply(embed=embed)

    def enc_or_dec(self, conversion_type, encoding, _input):
        if encoding not in self.encodings:
            raise commands.BadArgument(f"Invalid encoding. Valid encodings are: {', '.join(self.encodings)}")
        
        converter = getattr(base64, f"{encoding}{conversion_type}")
        output = str(converter(bytes(_input, "utf-8")))[2:-1]

        if len(output) > 1996:
            raise commands.BadArgument("The output is too long to send.")
        
        return output
    

async def setup(bot):
    await bot.add_cog(Utility(bot))