import asyncio
import re
import dis
import discord
from discord.ext import commands

class Calculator(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.calculatable = re.compile("^[\(\)0-9embt.\-\+\/*\/]+$")

    
    def subst_shorthands(self, calculation: str) -> str:
        def match_subst(match_obj: re.Match) -> str:
            match = match_obj.group(0)
            return f"({match[:-1]}{mapping[match[-1]]})"

        mapping = {"t": "*1000000000000", "b": "*1000000000", "m": "*1000000"}

        for pattern in mapping:
            calculation = re.sub(rf"\d+{pattern}", match_subst, calculation)
        
        return calculation
    
    @commands.Cog.listener("on_message")
    async def calculate(self, message: discord.Message):
        if message.author.bot:
            return
        
        if message.content.count("\n"):
            return
        
        trimmed_content = "".join(message.content.split())
        match = self.calculatable.match(trimmed_content)

        if match is None:
            return
        
        calculation = match.group()

        # no exponentiation or trying to create tuples
        if "**" in calculation or "()" in calculation:
            return
        
        # have at least one operation so we know the user is trying to calculate something
        if not {"*", "+", "-", "/"} & set(calculation):
            return
        
        # we do the substituion after checking for an operation
        calculation = self.subst_shorthands(calculation)

        try:
            codeobj = compile(calculation, "", "eval")
        except Exception as e:
            return

        # 100 -> LOAD_CONST, 83 -> RETURN_VALUE
        # adding redundancy just in case
        if [inst.opcode for inst in dis.get_instructions(codeobj)] != [100, 83]:
            return
        
        res = codeobj.co_consts[0]

        res = int(res) if isinstance(res, float) and res.is_integer() else res
        
        await message.add_reaction("\U00002795")
        
        def check(reaction: discord.Reaction, reactor: discord.Member) -> bool:
            return reactor == message.author and reaction.message == message and str(reaction.emoji) == "\U00002795"

        try:
            await self.bot.wait_for("reaction_add", check=check, timeout=15)
        except asyncio.TimeoutError:
            return
        
        embed = discord.Embed(title="Calculated:", description=f"Result: `{res:,}`", colour=0x303135)
        await message.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Calculator(bot))
