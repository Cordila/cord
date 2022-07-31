import discord
from discord.ext import commands
from core import checks
from core.models import PermissionLevel


class Owners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def dm(self, ctx, user: discord.Member, *, message):
        await user.send(f'Message from the staff team at `The Farm`: {message}')
        await ctx.channel.send("Sent the message")

    @commands.command(aliases=['ed'])
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def enabledisable(self, ctx):
        embed = discord.Embed(title="Enables/Disables",
                              description="`??disableautoban | ??enableautoban` \n \n `??disabledecancer | ??enabledecancer` \n \n `??disableextras | ??enableextras` \n \n `??disablelock | ??enablelock` \n \n `??disableping | ??enableping` \n \n `??disableshortcut | ??enableshortcut` \n \n `??disablesnipe | ??enablesnipe` \n \n `??disablesuggest | ??enablesuggest` \n \n `??disabletyperacer | ??enabletyperacer` \n \n `??disablear | ??enablear` \n \n `??disablecarl | ??enablecarl` \n \n `??disablesos | ??enablesos` \n \n `??disableselfroles | ??enableselfroles`")
        await ctx.send(embed=embed)

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def offline(self, ctx):
        """
        get all offline bots in a server
        """
        guild = ctx.guild
        offline_bots = []
        for member in guild.members:
            if not member.bot:
                continue
            if not member.status == discord.Status.offline:
                continue
            offline_bots.append(member)
        if not offline_bots:
            await ctx.send("No offline bots found")
            return
        await ctx.send(f"Found {len(offline_bots)} offline bots")
        for bot in offline_bots:
            await ctx.send(f"{bot.name}#{bot.discriminator}")


async def setup(bot):
    await bot.add_cog(Owners(bot))
