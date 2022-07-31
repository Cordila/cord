import asyncio
import discord
from discord.ext import commands

class SOSView(discord.ui.View):
    def __init__(self, bot:commands.Bot, player1: discord.Member, player2: discord.Member) -> None:
        self.bot = bot
        self.responses: dict[int, str | None] = {player1: None, player2: None}
        super().__init__(timeout=None)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user not in self.responses:
            await interaction.response.send_message("These aren't your buttons! >:(", ephemeral=True)
            return False
        
        if (choice := self.responses[interaction.user]) is not None:
            await interaction.response.send_message(f"You already chose **{choice}**!", ephemeral=True)
            return False
        
        return True

    @discord.ui.button(label="Split", style=discord.ButtonStyle.green)
    async def split(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.responses[interaction.user] = "split"

        await interaction.response.send_message("You chose **split**, let's hope the other person choses the same!", ephemeral=True)
        self.check_done_game()

    @discord.ui.button(label="Steal", style=discord.ButtonStyle.red)
    async def steal(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.responses[interaction.user] = "steal"

        await interaction.response.send_message("You chose **steal**, go big or go home!", ephemeral=True)
        self.check_done_game()
    
    def check_done_game(self) -> None:
        # stops the view when both players have responded
        if None not in self.responses.values():
            self.stop()
            self.bot.dispatch("sos_view_done", self.responses)

    async def edit_results(self, original_message: discord.Message) -> None:
        """This function is called after the view times out or finishes normally"""
        self.clear_items()
        embed = discord.Embed(title="Split or steal, pick wisely!",)

        # one or both players did not respond
        if None in self.responses.values():
            no_response = " and ".join(player.mention for player, resp in self.responses.items() if resp is None)
            embed.description = f"{no_response} did not respond in time D:"
        
        # the game is done!
        else:
            both_mentions = " and ".join(m.mention for m in self.responses)

            if all(resp == "split" for resp in self.responses.values()):
                embed.description = f"{both_mentions} both split, therefore the prize is divided equally between them!"
            
            elif all(resp == "steal" for resp in self.responses.values()):
                embed.description = f"{both_mentions} both stole, therefore neither of them get anything!"
            
            else:
                rev_mapping = {v:k for k,v in self.responses.items()}
                winner, loser = rev_mapping["steal"], rev_mapping["split"]

                embed.description = f"{winner.mention} stole, but {loser.mention} split, therefore {winner.mention} gets the prize!"
            
        await original_message.edit(embed=embed, view=self)

class SplitOrSteal(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    async def sos(self, ctx: commands.Context, player1: discord.Member, player2: discord.Member) -> None:
        embed = discord.Embed(title="Split or steal, pick wisely!", description="You have 60 seconds to decide")
        sos_view = SOSView(self.bot, player1, player2)
        original_message = await ctx.send(embed=embed, view=sos_view)

        # we need to do this since interactions which fail interaction_check still renews the timeout in the view
        try:
            await self.bot.wait_for("sos_view_done", check=lambda r: player1 in r and player2 in r, timeout=60)
        except asyncio.TimeoutError:
            pass
    
        await sos_view.edit_results(original_message)
    
    @sos.error
    async def sos_error(self, ctx: commands.Context, error) -> None:
        if isinstance(error, commands.MemberNotFound):
            return await ctx.reply("That's not a valid member")
        
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.reply("Usage: `??sos <player1> <player2>`")
        
async def setup(bot):
    await bot.add_cog(SplitOrSteal(bot))
