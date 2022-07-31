import discord
from pathlib import Path
from discord.ext import commands
from core import checks
from core.models import PermissionLevel

this_file_directory = Path(__file__).parent.resolve()
other_file = this_file_directory / "nosnipe.txt"
with open(other_file, "r+") as file:
    nosnipe = [nosnipe.strip().lower() for nosnipe in file.readlines()]


def check_view_perms(channel, member):
    return channel.permissions_for(member).view_channel


class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sniped = {}
        self.esniped = {}
        self.coll = bot.plugin_db.get_partition(self)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if any(word in message.content.lower() for word in nosnipe) or message.author.bot:
            return
        em = discord.Embed(description=message.content)
        em.set_author(name=message.author.display_name, icon_url=message.author.avatar)
        em.set_footer(text='Sent at: ')
        em.timestamp = message.created_at
        self.sniped[str(message.channel.id)] = em

    @commands.check_any(
        commands.is_owner(),
        commands.has_role('❋ Booster Rooster ❋'),
        commands.has_role('Satellite Supporter'),
        commands.has_role('⋯ ☆ ⋯ $10 Cash Donator ⋯ ☆ ⋯'),
        commands.has_role('Giveaway Manager'),
        commands.has_role('Heist Leader'),
        commands.has_role('Partner Manager'),
        commands.has_role('Farm Hand - Chat Moderator'),
        commands.has_role(682698693472026749),  # Daughter
        commands.has_role('Farmer - Head Moderator'),
        commands.has_role('Farm Manager - Server Admin'),
        commands.has_role('Level 20'),
        commands.has_role(753210431983583302),  # Secret Supporter
    )
    @commands.command()
    async def snipe(self, ctx, *, channel: discord.TextChannel = None):
        ch = channel or ctx.channel
        member = ctx.author
        fetch = await self.coll.find_one({"unique": "nosnipe"})
        chan = fetch['channels']
        if ctx.channel.id in chan:
            return 
        if check_view_perms(ch, member):
            if str(ch.id) not in self.sniped:
                return await ctx.send('There\'s nothing to be sniped!')
            return await ctx.send(embed=self.sniped[str(ch.id)])
        else:
            await ctx.send("You arent supposed to see whats going on here!")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if any(word in before.content.lower() for word in nosnipe) or any(word in after.content.lower() for word in
                                                                          nosnipe) or before.author.bot or before.content == after.content:
            return

        em = discord.Embed(description=f'**Before: ** {before.content}\n**After: ** {after.content}')
        em.set_author(name=before.author.display_name, icon_url=before.author.avatar)
        em.set_footer(text='Sent at: ')
        em.timestamp = before.created_at
        self.esniped[str(before.channel.id)] = em

    @commands.check_any(
        commands.is_owner(),
        commands.has_role('❋ Booster Rooster ❋'),
        commands.has_role('Satellite Supporter'),
        commands.has_role('⋯ ☆ ⋯ $10 Cash Donator ⋯ ☆ ⋯'),
        commands.has_role('Giveaway Manager'),
        commands.has_role('Heist Leader'),
        commands.has_role('Partner Manager'),
        commands.has_role('Farm Hand - Chat Moderator'),
        commands.has_role(682698693472026749),  # Daughter
        commands.has_role('Farmer - Head Moderator'),
        commands.has_role('Farm Manager - Server Admin'),
        commands.has_role('Level 20'),
        commands.has_role(753210431983583302),  # Secret Supporter
    )
    @commands.command()
    async def esnipe(self, ctx, *, channel: discord.TextChannel = None):
        ch = channel or ctx.channel
        member = ctx.author
        fetch = await self.coll.find_one({"unique": "nosnipe"})
        chan = fetch['channels']
        if ctx.channel.id in chan:
            return 
        if check_view_perms(ch, member):
            if str(ch.id) not in self.esniped:
                return await ctx.send('There\'s nothing to be sniped!')
            return await ctx.send(embed=self.esniped[str(ch.id)])
        else:
            await ctx.send("You arent supposed to see whats going on here!")

    @commands.group(invoke_without_command=True)
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def snipes(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("You are probably looking for `??snipes config`")

    @snipes.group(invoke_without_command=True)
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def config(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Config options: \n `nosnipe` - Make the channel unsnipeable \n `yessnipe` - Make the channel snipeable again")

    @config.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def nosnipe(self, ctx, channel: discord.TextChannel = None):
        c = ""
        if channel is None:
            fetch = await self.coll.find_one({"unique": "nosnipe"})
            chan = fetch["channels"]
            for chaid in chan:
                chai = self.bot.get_channel(chaid)
                c += f"{chai.mention}, "
            return await ctx.send(f'Snipe doesnt work in \n {c}')
        check = await self.coll.find_one({'channels': channel.id})
        if check:
            return await ctx.send('This channel is already unsnipeable!')
        await self.coll.find_one_and_update({"unique": "nosnipe"}, {"$push": {"channels": channel.id}}, upsert=True)
        await ctx.send(f'{channel.mention} is no longer snipeable!')

    @config.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def yessnipe(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            return await ctx.send('Please specify a channel where you want snipe to work!')
        check = await self.coll.find_one({'channels': channel.id})
        if not check:
            return await ctx.send('This channel is already snipeable!')
        await self.coll.find_one_and_update({"unique": "nosnipe"}, {"$pull": {"channels": channel.id}})
        await ctx.send(f'{channel.mention} is now snipeable!')


async def setup(bot):
    await bot.add_cog(Snipe(bot))
