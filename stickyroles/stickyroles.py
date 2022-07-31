from discord.ext import commands
import discord


class StickyRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coll = bot.plugin_db.get_partition(self)

    async def add_sticky(self, unique, role: discord.Role):
        await self.coll.find_one_and_update({"unique": unique}, {"$push": {"role_id": role.id}}, upsert=True)

    async def remove_sticky(self, unique, role: discord.Role):
        await self.coll.find_one_and_update({"unique": unique}, {"$pull": {"role_id": role.id}})

    @commands.command()
    async def addsticky(self, ctx, role: discord.Role):
        """Adds a sticky role to the database"""
        check = await self.coll.find_one({"role_id": role.id})
        if check:
            return await ctx.send("This role is already a sticky role")
        await self.add_sticky("1", role)
        await ctx.send(f"Added `{role.name}` to the sticky roles")

    @commands.command()
    async def removesticky(self, ctx, role: discord.Role):
        """Removes a sticky role from the database"""
        check = await self.coll.find_one({"role_id": role.id})
        if not check:
            return await ctx.send("This role is not a sticky role")
        await self.remove_sticky("1", role)
        await ctx.send(f"Removed `{role.name}` from the sticky roles")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        s = []
        for role in member.roles:
            check = await self.coll.find_one({"role_id": role.id})
            if check:
                s.append(role.id)
        await self.coll.insert_one({"member_id": member.id, "role_id": s})

    @commands.Cog.listener()
    async def on_member_join(self, member):
        check = await self.coll.find_one({"member_id": member.id})
        if check:
            for role in check["role_id"]:
                sticky = member.guild.get_role(role)
                await member.add_roles(sticky)
            await self.coll.delete_one({"member_id": member.id})


async def setup(bot):
    await bot.add_cog(StickyRoles(bot))
