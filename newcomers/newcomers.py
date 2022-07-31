import discord
import re
from datetime import datetime, timedelta
from discord.ext import commands
from discord.ext import tasks
from core import checks
from core.models import PermissionLevel

time_units = {'s': 'seconds', 'm': 'minutes', 'h': 'hours', 'd': 'days', 'w': 'weeks'}


def to_seconds(s):
    return int(timedelta(**{
        time_units.get(m.group('unit').lower(), 'seconds'): int(m.group('val'))
        for m in re.finditer(r'(?P<val>\d+)(?P<unit>[smhdw]?)', s, flags=re.I)
    }).total_seconds())


class NewComers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coll = bot.plugin_db.get_partition(self)
        self.checker.start()
        self.updater.start()

    async def tempban(self, user: discord.Member, seconds):
        text = seconds
        in_seconds = {'h': 3600, 'm': 60, 's': 1, ' ': 1}
        seconds = sum(int(num) * in_seconds[weight if weight else 's'] for num, weight in
                      re.findall(r'(\d+)\s?(msh)?', text))
        current_time = datetime.utcnow()
        final_time = current_time + timedelta(seconds=seconds)
        tempbanned = {"user_id": user.id, "BannedUntil": final_time}
        await self.coll.insert_one(tempbanned)

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def dontunban(self, ctx, user: discord.User):
        dontunban = await self.coll.find_one({"user_id": user.id})
        await self.coll.delete_one(dontunban)
        await ctx.send("I wont unban them, thanks.")

    @commands.Cog.listener()
    async def on_member_join(self, user: discord.Member):
        frozencheck = await self.bot.db.plugins.Decancer.find_one({"user_id": str(user.id)})
        now = discord.utils.utcnow()
        age = now - user.created_at
        days = age.days
        channel = self.bot.get_channel(995433424963764254)
        
        if frozencheck:
            frozennick = frozencheck['Nickname']
            await user.edit(nick=frozennick)
            await channel.send(f"Auto Froze {user} `{user.id}` to `{frozennick}` because they previously had a frozen nickname")

        if days == 0:
            await self.tempban(user, str((90 - days) * 24 * 60 * 60))
            await user.ban(reason="Suspected ALT, Banned for 90 days.")
            await channel.send(
                f"Auto Banned {user} `{user.id}` for being a suspected ALT, Come back in {(90 - days)} days")

        elif days < 14:
            await self.tempban(user, str((14 - days) * 24 * 60 * 60))
            await user.ban(
                reason="Your account is too new! Feel free to join back when your account is atleast 15 days old. discord.gg/dank")
            await channel.send(
                f"Auto banned {user} `{user.id}` for being younger than 14d. Come back in {(14 - days)} days")

    @tasks.loop(minutes=30)
    async def checker(self):
        try:
            fetchall = await self.coll.find().sort('BannedUntil', 1).to_list(5)  # return first 5
            current_time = datetime.utcnow()
            for x in fetchall:
                if current_time >= x["BannedUntil"]:  # do stuff after this
                    unbanuser = x["user_id"]
                    member = discord.Object(id=unbanuser)
                    guild = self.bot.get_guild(645753561329696785)
                    try:
                        await guild.unban(member, reason="Tempban for new account expired.")
                        deletetime = await self.coll.find_one({"user_id": int(unbanuser)})
                        await self.coll.delete_one(deletetime)
                    except Exception as e:
                        print(e)
                        deletetime = await self.coll.find_one({"user_id": int(unbanuser)})
                        await self.coll.delete_one(deletetime)

        except Exception as e:
            print(e)
            
    @tasks.loop(hours=1)
    async def updater(self):
        guild = self.bot.get_guild(645753561329696785)
        channel = self.bot.get_channel(696433564232974339)
        count = f"Members: {guild.member_count}"
        await channel.edit(name=count)
        
async def setup(bot):
    await bot.add_cog(NewComers(bot))
