import discord
from discord.ext import commands
from core import checks
from core.models import PermissionLevel


class Shortcuts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def dmads(self, ctx, user: discord.User, proof, proof2=None):
        if proof2 is None:
            await ctx.send(
                f'```.ban {user.id} DM [Advertisements]({proof}) are against the rules of the server. Appeal this ban at https://discord.gg/appeal ```')
        else:
            await ctx.send(
                f'```.ban {user.id} DM Advertisements are against the rules of the server. Proof: [1]({proof}), [2]({proof2}). Appeal this ban at https://discord.gg/appeal```')

async def setup(bot):
    await bot.add_cog(Shortcuts(bot))
