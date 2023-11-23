import discord, os, json, asyncio
from discord.ext import commands
from discord.ext.commands.context import Context
from utils import separate

class Manager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx):
        return self.bot.checks.is_manager(ctx)
    
    @commands.command(aliases=["ul"])
    async def unload(self, ctx, extension: str = "all"):
        await self.handle_cog(ctx, self.bot.unload_extension, extension)

    @commands.command(aliases=["rl", "rel"])
    async def reload(self, ctx, extension: str = "all"):
        await self.handle_cog(ctx, self.bot.reload_extension, extension)

    @commands.command()
    async def load(self, ctx, extension: str):
        await self.handle_cog(ctx, self.bot.load_extension, extension)

    @commands.command()
    async def shutdown(self, ctx):
        await ctx.send("Shutting down...")
        await self.bot.logout()

    async def handle_cog(self, ctx, func, extension):
        extension = extension.lower()

        func_name = {
            "unload_extension": "unload",
            "reload_extension": "reload",
            "load_extension": "load"
        }[func.__name__]

        if extension == "all":
            message = ""
            for i, file in enumerate(os.listdir("./cogs")):
                if file.endswith(".py"):
                    file = file[:-3]
                    try:
                        func(f"cogs.{file}")
                        message += f"+ [{i}] cog \"{file}\" {func_name}ed successfully\n"
                    except Exception as e:
                        message += f"- [{i}] unable to {func_name} cog \"{file}\". {e.__class__.__name__}: {e}\n"
            
            embed = discord.Embed(description=f"```diff\n{message}```")
            return await ctx.reply(embed=embed)
        
        try:
            func(f"cogs.{extension}")
            embed = discord.Embed(description=f"```diff\n+ cog \"{extension}\" {func_name}ed successfully\n```")
            await ctx.reply(embed=embed)
        except Exception as e:
            embed = discord.Embed(description=f"```diff\n- unable to {func_name} cog \"{extension}\". {e.__class__.__name__}: {e}\n```")
            await ctx.reply(embed=embed)
        

async def setup(bot):
    await bot.add_cog(Manager(bot))