import discord
import typing

from discord.ext import commands
from core import checks
from core.models import PermissionLevel


class Autoreact(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coll = bot.plugin_db.get_partition(self)

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def addar(self, ctx, member: discord.Member, emoji: typing.Union[discord.Emoji, str]):
        check = await self.coll.find_one({"user_id": member.id})
        if check:
            return await ctx.send("The autoreact already exists for this user")
        emoji1 = str(emoji)
        ar = {"user_id": member.id, "reaction": emoji1}
        await self.coll.insert_one(ar)
        await ctx.send(f"Added reaction {emoji} for {member.mention}")

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def removear(self, ctx, user: discord.User):
        ar = await self.coll.find_one({"user_id": user.id})
        if not ar:
            return await ctx.send("This user doesnt have an autoreact anyways whatcha up to?")
        reaction1 = ar["reaction"]
        await self.coll.delete_one(ar)
        await ctx.send(f"Deleted reaction {reaction1} for {user.name}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        for x in message.mentions:
            uid = await self.coll.find_one({"user_id": x.id})  # getting the user ID if in db then getting reaction
            if not uid:
                return
            reaction1 = uid["reaction"]
            await message.add_reaction(reaction1)

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def getars(self, ctx):
        s = ""
        fetchall = self.coll.find({})
        async for x in fetchall:
            convert = x['user_id']
            converted = self.bot.get_user(convert)
            s += f"{converted} (`{convert}`) : {x['reaction']} \n"

        stuff = s.splitlines()
        for i in range(0, len(stuff), 25):
            chunk = stuff[i:i + 25]
            final = "\n".join(chunk)
            await ctx.send(final)


async def setup(bot):
    await bot.add_cog(Autoreact(bot))
