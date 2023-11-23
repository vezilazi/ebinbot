import os, json
from datetime import datetime as dt

def dt_format(dt_obj):
    return dt_obj.strftime("%Y-%m-%d %H:%M:%S")


def requested(ctx):
    name = f"Requested by {ctx.author.name}"
    icon_url = ctx.author.avatar_url
    return {"name": name, "icon_url": icon_url}


def get_config():
    config_path = f"{os.path.realpath(os.path.dirname(__file__))}/../config/config.json"
    if not os.path.exists(config_path):
        with open(config_path, "w") as file:
            json.dump(
                {
                    "token": "",
                    "prefix": ">",
                    "invite_link": "",
                    "support_server": "",
                    "managers": [],
                },
                file,
                indent=4,
            )
        print("Please fill out config.json")
        exit()
    else:
        with open(config_path) as file:
            config = json.load(file)
    return config

def guild_repr(ctx):
    gld = ctx.guild
    bots = 0
    emj, a_emj = 0, 0
    created = gld.created_at
    for emoji in gld.emojis:
        if emoji.animated: a_emj += 1
        else: emj += 1
    
    statuses = {k: 0 for k in ["online", "idle", "dnd", "offline"]}
    for member in ctx.guild.members:
        statuses[str(member.status)] += 1
        if member.bot: bots += 1

    description = f"```yaml\n" \
    f"---\n- name: {gld.name}\n- owner: {gld.owner.name} ({gld.owner.id})\n- id: {gld.id}\n" \
    f"- created: {dt_format(created)} (~{(dt.utcnow() - created).days()} days)\n" \
    f"---\n- members: {gld.member_count - bots} humans, {bots} bots\n- roles: {len(gld.roles)}\n- emojis: {emj} static, {a_emj} animated\n" \
    f"---\n- text channels: {len(gld.text_channels)}\n- voice channels: {len(gld.voice_channels)}\n" \
    f"- verif. level: {gld.verification_level}\n- region: {gld.region}\n---\n```" \
    f"\n**__online statuses__**\n" \
    f"```diff\n+ online: {statuses['online']}\n```\n```md\n< idle: {statuses['idle']}```\n" \
    f"```diff\n- dnd: {statuses['dnd']}\n```\n```md\n> offline: {statuses['offline']}\n```"

    return description


def separate(lis, n):
    dm = divmod(len(lis), n)
    s = [[] for i in range(dm[0] + bool(dm[1]))]
    for i, item in enumerate(lis):
        n = i % len(s)
        s[n].append(item)
    return s