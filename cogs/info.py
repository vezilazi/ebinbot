import discord, time, asyncio
from discord.ext import commands
from utils import dt_format, requested, separate, guild_repr
from datetime import datetime as dt

from prettytable import PrettyTable as PT

PERMS_LIST = ['add_reactions', 'administrator', 'attach_files', 'ban_members',
              'change_nickname', 'connect', 'create_instant_invite', 'deafen_members',
              'embed_links', 'external_emojis', 'kick_members', 'manage_channels',
              'manage_emojis', 'manage_guild', 'manage_messages', 'manage_nicknames',
              'manage_permissions', 'manage_roles', 'manage_webhooks', 'mention_everyone',
              'move_members', 'mute_members', 'priority_speaker', 'read_message_history',
              'read_messages', 'send_messages', 'send_tts_messages', 'speak', 'stream',
              'use_external_emojis', 'use_voice_activation', 'view_audit_log',
              'view_channel', 'view_guild_insights']


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """Get the bot's latency"""
        before = time.monotonic()
        before_ws = int(round(self.bot.latency * 1000, 3))
        msg = await ctx.send("Pinging...")
        _ping = (time.monotonic() - before) * 1000

        embed = discord.Embed(title="Latency", description=f"```yaml\nWS:\n  - {before_ws}ms\n\nREST:\n  - {_ping}ms```")
        await msg.edit(content="", embed=embed)

    @commands.command(aliases=["perms"])
    async def permissions(self, ctx, *, member: discord.Member = None):
        """Get a member's permissions"""
        member = member or ctx.author
        perms = member.guild_permissions

        message = ""
        embed = discord.Embed(title=f"Permissions for {member}")
        for perm in PERMS_LIST:
            if getattr(perms, perm):
                message += f"  - {perm.replace('_', ' ')}\n"
        
        embed.description = f"```yaml\nall perms set to true:\n{message}\n```"
        embed.set_footer(text=f"Permissions code: {perms.value}")
        if not message:
            embed.description = "```yaml\nNo perms set to true```"
        
        await ctx.send(embed=embed)

    @commands.command(aliases=["rperms"])
    async def roleperms(self, ctx, *, role: discord.Role):
        perms = role.permissions

        message = ""
        embed = discord.Embed(title=f"Permissions for {role.name} role")
        for perm in PERMS_LIST:
            if getattr(perms, perm):
                message += f"  - {perm.replace('_', ' ')}\n"

        embed.description = f"```yaml\nall perms set to true:\n{message}\n```"
        embed.set_footer(text=f"Permissions code: {perms.value}")
        if not message:
            embed.description = "```yaml\nNo perms set to true```"

        await ctx.send(embed=embed)

    @commands.command(aliases=["roles"])
    async def rolestats(self, ctx):
        roles = ctx.guild.roles
        role_groups = separate(roles, 30)
        for i, rg in enumerate(role_groups):
            pt = PT()
            pt.field_names = ["role", "members", "%"]
            pt.align = "l"
            embed = discord.Embed()
            for role in rg:
                name = role.name[:15] + ("..." if len(role.name) > 15 else "")
                members = len(role.members)
                percentage = len(role.members) / len(ctx.guild.members) * 100

                pt.add_row([name, members, f"{percentage:.2f}%"])

            if i == 0: embed.title = f"Role stats for {ctx.guild}"
            embed.description = f"```\n{pt}\n```"
            await ctx.send(embed=embed)
            await asyncio.sleep(0.51)

    @commands.command(aliases=["inv"])
    async def invite(self, ctx):
        """Get the bot's invite link"""
        embed = discord.Embed(title="Invite link")
        embed.description = f"[Click here]({self.bot.config['invite_link']}) to invite me to your server!"
        embed.set_image(url=self.bot.user.avatar_url)
        await ctx.reply(embed=embed)

    @commands.command(aliases=["who"])
    @commands.guild_only()
    async def whois(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author

        now = dt.utcnow()
        acc_age = (now - member.created_at).days
        since_join = (now - member.joined_at).days

        activity = member.activity
        if activity:
            _type = str(activity.type).replace("ActivityType.", "")
            _type = (f"{_type} " if not _type == "custom" else "").title()
            activity = _type + str(activity.name)

        message = \
        f"created: {dt_format(member.created_at)} (~{acc_age} days)\n" \
        f"joined: {dt_format(member.joined_at)} (~{since_join} days)\n---\n" \
        f"display: {member.display_name}\n" \
        f"top role: {member.top_role} ({member.top_role.id})\n" \
        f"role count: {len(member.roles)}\n---\n" \
        f"bot: {member.bot}\n" \
        f"online status: {member.status}\n" \
        f"custom status: {activity}"

        embed = discord.Embed(
            title=f"Info for {member}",
            description=f"```yaml\n---\n{message}\n---\n```"
        )
        embed.set_image(url=member.avatar_url)
        embed.set_author(**requested(ctx))
        embed.set_footer(text=f"ID: {member.id}")
        await ctx.send(embed=embed)

    @commands.command(aliases=["av", "ava", "pfp"])
    @commands.guild_only()
    async def avatar(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        await ctx.reply(member.avatar_url)

    @commands.command(aliases=["role"])
    @commands.guild_only()
    async def roleinfo(self, ctx, *, role: discord.Role):
        created = f"created: {dt_format(role.created_at)} (~{(dt.utcnow() - role.created_at).days} days)"
        members, percentage = len(role.members), len(role.members) / len(ctx.guild.members) * 100
        members = f"members: {members} | {percentage:.2f}%"
        attrs = ["colour", "position", "id", "mentionable"]
        attrs = "\n".join([f"{attr}: {getattr(role, attr)}" for attr in attrs])

        embed = discord.Embed(title=f"Info for {role.name}", colour=role.colour)
        embed.set_author(**requested(ctx))
        embed.description = f"```yaml\---\n{created}\n---\n{members}\n---\n{attrs}\n---\n```"
        await ctx.send(embed=embed)

    @commands.command(aliases=["server", "guild", "guildinfo"])
    @commands.guild_only()
    async def serverinfo(self, ctx):
        embed = discord.Embed(title=f"Info for {ctx.guild}")
        embed.description = guild_repr(ctx)
        embed.set_author(**requested(ctx))
        embed.set_image(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.guild_only()
    async def emojis(self, ctx):
        lis = separate(ctx.guild.emojis, 64)
        if not lis:
            return await ctx.reply("This server has no emojis!")
        
        for i in lis:
            embed = discord.Embed(description=" ".join(list(map(str, i))))
            await ctx.send(embed=embed)
            await asyncio.sleep(0.51)

    @commands.command(aliases=["bot"])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def botstats(self, ctx):
        owner = (await self.bot.application_info()).owner
        description = \
        f"---\nname: {self.bot.user.name}\nid: {self.bot.user.id}\n" \
        f"guilds: {len(self.bot.guilds)}\nusers: {len(self.bot.users)}\n" \
        f"---\ncommands: {len(self.bot.commands)}\nlib: discord.py\n---"

        embed = discord.Embed(title="Bot stats")
        embed.set_footer(text=f"Owner: {owner}", icon_url=owner.avatar_url)
        embed.set_image(url=self.bot.user.avatar_url)
        embed.description = f"```yaml\n{description}\n```"

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Info(bot))