import discord, aiohttp
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel = bot.get_channel(1174286233107714098)
        self.meme = None

    async def get_meme(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://www.reddit.com/r/dankmemes/top/.json?sort=top&t=day&limit=1") as response:
                if response.status == 200:
                    json = await response.json()
                    self.meme = json["data"]["children"][0]["data"]
                else:
                    print("Error getting meme")
    
    async def send_meme(self):
        if self.meme is None:
            await self.get_meme()
        if self.channel is None:
            self.channel = self.bot.get_channel(1174286233107714098)
        embed = discord.Embed(title=self.meme["title"], color=0x00FF00)
        embed.set_image(url=self.meme["url"])
        embed.set_footer(text=f"👍 {self.meme['ups']} | 💬 {self.meme['num_comments']}")
        await self.channel.send(embed=embed)
    
    @commands.command()
    async def meme(self, ctx):
        """Sends a meme"""

        embed = discord.Embed(title="Meme", description="Sending meme...", color=0x00FF00)
        await ctx.send(embed=embed)
        await self.send_meme()


async def setup(bot):
    await bot.add_cog(Fun(bot))