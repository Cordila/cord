import discord
import re
from discord.ext import commands
from datetime import timedelta


def to_seconds(s):
    return int(
        timedelta(**{
            {
                's': 'seconds', 'm': 'minutes', 'h': 'hours', 'd': 'days', 'w': 'weeks'
            }.get(m.group('unit').lower(), 'seconds'): int(m.group('val'))
            for m in re.finditer(r'(?P<val>\d+)(?P<unit>[smhdw]?)', s, flags=re.I)
        }
                  ).total_seconds())


class LockAndSlow(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_any_role(682698693472026749, 658770981816500234, 663162896158556212, 658770586540965911,
                           814004142796046408, 855877108055015465)
    async def lock(self, ctx, channel: discord.TextChannel = None):
        if not channel:
            channel = ctx.channel

        allowed_channels = [995563300618240100, 995563935874949160, 756552586248585368, 747853054329487500]
        if ctx.author.top_role.id in (855877108055015465, 814004142796046408):
            if channel.id in allowed_channels:
                if channel.overwrites_for(ctx.guild.default_role).send_messages is None or channel.overwrites_for(
                        ctx.guild.default_role).send_messages is True:
                    await channel.set_permissions(ctx.guild.default_role, send_messages=False)
                    await ctx.send(f"🔒 Locked `{channel}`")
                else:
                    await ctx.send(f"🔒 Looks like `{channel}` is already locked")
            else:
                await ctx.send(f"You are not allowed to lock {channel}")

        elif {658770981816500234, 682698693472026749, 658770586540965911, 663162896158556212} & set(ctx.author.roles):
            if channel.overwrites_for(ctx.guild.default_role).send_messages is None or channel.overwrites_for(
                    ctx.guild.default_role).send_messages is True:
                await channel.set_permissions(ctx.guild.default_role, send_messages=False)
                await ctx.send(f"🔒 Locked `{channel}`")
            else:
                await ctx.send(f"🔒 Looks like `{channel}` is already locked")

    @commands.command()
    @commands.has_any_role(682698693472026749, 658770981816500234, 663162896158556212, 658770586540965911,
                           814004142796046408, 855877108055015465)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        if not channel:
            channel = ctx.channel

        allowed_channels = [995563300618240100, 995563935874949160, 756552586248585368, 747853054329487500]
        if ctx.author.top_role.id in (855877108055015465, 814004142796046408):
            if channel.id in allowed_channels:
                if not channel.overwrites_for(ctx.guild.default_role).send_messages:
                    await channel.set_permissions(ctx.guild.default_role, send_messages=True)
                    await ctx.send(f"🔒 Unlocked `{channel}`")
                else:
                    await ctx.send(f"🔒 Looks like `{channel}` is already unlocked")
            else:
                await ctx.send(f"You are not allowed to unlock {channel}")

        elif {658770981816500234, 682698693472026749, 658770586540965911, 663162896158556212} & set(ctx.author.roles):
            if not channel.overwrites_for(ctx.guild.default_role).send_messages:
                await channel.set_permissions(ctx.guild.default_role, send_messages=True)
                await ctx.send(f"🔒 Unlocked `{channel}`")
            else:
                await ctx.send(f"🔒 Looks like `{channel}` is already unlocked")

    @commands.command(aliases=['slowmode', 'slow'])
    @commands.has_permissions(manage_messages=True)
    async def sm(self, ctx, delay):
        slomo_embed = discord.Embed(
            title=f" A slowmode of {delay} has been activated by a moderator.",
            color=0x363940, timestamp=ctx.message.created_at)
        slomo_embed.set_footer(text=f'Applied by {ctx.author}', icon_url=ctx.author.avatar)
        await ctx.message.delete()
        await ctx.channel.edit(slowmode_delay=to_seconds(delay))
        await ctx.send(content=None, embed=slomo_embed)

    @commands.command()
    async def slownow(self, ctx):
        await ctx.send(f' The current slow mode in the channel is {ctx.channel.slowmode_delay} seconds')


async def setup(bot):
    await bot.add_cog(LockAndSlow(bot))
