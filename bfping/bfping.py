import discord
import asyncio
from discord.ext import commands
import re

time_units = {'s': 'seconds', 'm': 'minutes', 'h': 'hours', 'd': 'days', 'w': 'weeks'}


class BFPing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def gaw(self, ctx, *, messages="^_^"):
        if ctx.message.raw_role_mentions or '@everyone' in ctx.message.content or '@here' in ctx.message.content:
            gwm = ctx.guild.get_role(855877108055015465)
            await ctx.author.remove_roles(gwm)
            return await ctx.send("Pretty sure you don't want to do that man")
        if ctx.channel.id == 995523637249585202:
            await ctx.channel.purge(limit=1)
            await ctx.send(f'<@&672889430171713538> {messages}')
        else:
            await ctx.send('You can only use this command in <#995523637249585202>')

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def partner(self, ctx, *, messages="^_^"):
        if ctx.message.raw_role_mentions or '@everyone' in ctx.message.content or '@here' in ctx.message.content:
            partner = ctx.guild.get_role(790290355631292467)
            await ctx.author.remove_roles(partner)
            return await ctx.send("Pretty sure you don't want to do that man")
        if ctx.channel.id == 688431055489073180:
            await ctx.channel.purge(limit=1)
            await ctx.send(f'<@&793454145897758742> {messages}')
        else:
            await ctx.send('You can only use this command in <#688431055489073180>')

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def heist(self, ctx, *, messages="^_^"):
        if ctx.message.raw_role_mentions or '@everyone' in ctx.message.content or '@here' in ctx.message.content:
            heist = ctx.guild.get_role(723035638357819432)
            await ctx.author.remove_roles(heist)
            return await ctx.send("Pretty sure you don't want to do that man")
        if ctx.channel.id == 688581086078304260:
            await ctx.channel.purge(limit=1)
            await ctx.send(f'<@&684987530118299678> {messages}')
        else:
            await ctx.send('You can only use this command in <#688581086078304260>')

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def ev(self, ctx, *, messages="^_^"):
        if ctx.message.raw_role_mentions or '@everyone' in ctx.message.content or '@here' in ctx.message.content:
            gwm = ctx.guild.get_role(855877108055015465)
            await ctx.author.remove_roles(gwm)
            return await ctx.send("Pretty sure you don't want to do that man")
        if ctx.channel.id == 995556725694402691:
            await ctx.channel.purge(limit=1)
            await ctx.send(f'<@&684552219344764934> {messages}')
        else:
            await ctx.send('You can only use this command in <#995556725694402691>')

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def friendly(self, ctx, *, messages="^_^"):
        if ctx.message.raw_role_mentions or '@everyone' in ctx.message.content or '@here' in ctx.message.content:
            gwm = ctx.guild.get_role(855877108055015465)
            await ctx.author.remove_roles(gwm)
            return await ctx.send("Pretty sure you don't want to do that man")
        if ctx.channel.id == 995556725694402691:
            await ctx.channel.purge(limit=1)
            await ctx.send(f'<@&750908803704160268> {messages}')
        else:
            await ctx.send('You can only use this command in <#995556725694402691>')

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def lot(self, ctx, *, message="^_^"):
        if ctx.message.raw_role_mentions or '@everyone' in ctx.message.content or '@here' in ctx.message.content:
            gwm = ctx.guild.get_role(855877108055015465)
            await ctx.author.remove_roles(gwm)
            return await ctx.send("Pretty sure you don't want to do that man")
        if ctx.channel.id == 732604674108030987:
            await ctx.channel.purge(limit=1)
            await ctx.send(f' <@&732949595633614938> {message}')
        else:
            await ctx.send('You can only use this command in <#732604674108030987>')

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def maf(self, ctx, *, messages="^_^"):
        if ctx.message.raw_role_mentions or '@everyone' in ctx.message.content or '@here' in ctx.message.content:
            gwm = ctx.guild.get_role(855877108055015465)
            await ctx.author.remove_roles(gwm)
            return await ctx.send("Pretty sure you don't want to do that man")
        if ctx.channel.id == 756566417456889965:
            await ctx.channel.purge(limit=1)
            await ctx.send(f'<@&713898461606707273> {messages}')
        else:
            await ctx.send('You can only use this command in <#756566417456889965>')

    @staticmethod
    def to_seconds(s):
        return int(timedelta(**{
            time_units.get(m.group('unit').lower(), 'seconds'): int(m.group('val'))
            for m in re.finditer(r'(?P<val>\d+)(?P<unit>[smhdw]?)', s, flags=re.I)
        }).total_seconds())

    @commands.command()
    @commands.has_any_role(682698693472026749, 663162896158556212, 658770981816500234, 855877108055015465)
    async def esponsor(self, ctx, member: discord.Member, seconds=None):
        role = ctx.guild.get_role(787572079573598220)
        if seconds is None:
            if role in member.roles:            
                await member.remove_roles(role)
                await ctx.send("The role has been removed from them!")
            else:
                await ctx.send("Please specify a time. Eg. `3m`")
        try:
            text = seconds
            seconds = sum(
                int(num) * {'h': 60 * 60, 'm': 60, 's': 1, ' ': 1}[weight if weight else 's'] for num, weight in
                re.findall(r'(\d+)\s?([msh])?', text))

            if not 59 < seconds < 3601:
                await ctx.message.reply("Please keep the time between 1 minute and 1 hour.")
                raise BaseException

            if role not in member.roles:
                await member.add_roles(role)
                await ctx.send("The role has been added")
                await asyncio.sleep(seconds)
                if role in member.roles:
                    await member.remove_roles(role)
                    await ctx.send(f"The Event Sponsor role has has been removed from {member.mention}")
        except ValueError:
            await ctx.message.reply('You must enter a number!')


async def setup(bot):
    await bot.add_cog(BFPing(bot))
