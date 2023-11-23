from typing import Any, List, Mapping, Optional
import discord
from discord.ext import commands
from discord.ext.commands import Context
from discord.ext.commands.cog import Cog
from discord.ext.commands.core import Command
import utils

VISIBLE_COGS = ["info", "utility", "music", "embed"]

class HelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        desc = []
        for cog, cmds in mapping.items():
            if cog is None or cog.qualified_name.lower() not in VISIBLE_COGS:
                continue

            name = cog.qualified_name
            cmds = await self.filter_commands(cmds, sort=True)

            desc.append(f"{name}: {len(cmds)} commands")

        desc = "\n-\n".join(desc)

        embed = discord.Embed(title="All Commands")
        embed.description = f"```yaml\n---\n{desc}\n---\n```"
        embed.set_footer(text=f"Use {self.context.prefix}{self.invoked_with} [cog] to learn more about a cog and its commands.")
        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group, context: Context):
        desc = ""
        cmds = await self.filter_commands(group.commands, sort=True)
        for c in cmds:
            desc += f"{c.qualified_name}: {c.short_doc or 'no description'}\n"

        embed = discord.Embed(title=f"Help for {group.qualified_name}")
        embed.description = f"```yaml\n---\n{desc}\n---\n```"
        embed.set_footer(text=f"Use {context.clean_prefix}{self.invoked_with} [command] to learn more about a command.")
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, cmd):
        desc = \
        f"name: {cmd.name}\ncog: {cmd.cog_name}\ndescription:\n {cmd.help or cmd.short_doc or 'no description'}\n\n" \
        f"aliases:\n - {', '.join(cmd.aliases) if cmd.aliases else 'none'}\n\n" \
        f"usage: {cmd.name} {cmd.signature}"

        embed = discord.Embed(title=f"Help for {cmd.qualified_name}")
        embed.description = f"```yaml\n---\n{desc}\n---\n```"
        embed.set_footer(text="[] = required, () = optional")
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        cmds = await self.filter_commands(cog.get_commands(), sort=True)
        cmds = "\n-\n".join(f"{cmd.name}: {cmd.help}" for cmd in cmds)
        embed = discord.Embed(title=f"Help for {cog.qualified_name}")
        embed.description = f"```yaml\n---\n{cmds}\n---\n```"
        embed.set_footer(text=f"Use {self.context.prefix}{self.invoked_with} [command] to learn more about a command.")
        await self.get_destination().send(embed=embed)


async def setup(bot):
    bot.__default_help_command__ = bot.help_command
    bot.help_command = HelpCommand()


def teardown(bot):
    bot.help_command = bot.__default_help_command__