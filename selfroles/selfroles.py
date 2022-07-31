from typing import Sequence
from discord.ext import commands
import discord
from .selfroles_data import REGULAR_COLOURS, PREMIUM_COLOURS, ACCESS, PING, REGION, AGE, GENDER
from .core import RoleHelper, GenericRoleButton

Roles = dict[int, str]

class SelfRoles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    
    async def cog_load(self) -> None:
        await self.bot.wait_until_ready()
        
        # colours
        colours = REGULAR_COLOURS.copy()
        colours.update(PREMIUM_COLOURS)

        self.colour_view = RoleHelper.get_view(colours, btn_callback=self.check_colour_roles)

        # access
        self.access_view = RoleHelper.get_view(ACCESS)

        # ping
        self.ping_view = RoleHelper.get_view(PING, btn_callback=self.check_ping_roles)

        # region
        self.region_view = RoleHelper.get_view(REGION, btn_callback=self.check_region_roles)

        # age
        self.age_view = RoleHelper.get_view(AGE, btn_callback=self.check_age_roles)

        # gender
        self.gender_view = RoleHelper.get_view(GENDER, btn_callback=self.check_gender_roles)

        for view in [self.colour_view, self.access_view, self.ping_view, self.region_view, self.age_view, self.gender_view]:
            # making all the views persistent
            self.bot.add_view(view)
        
    async def remove_roles(self, member: discord.Member, roles: Sequence[int]) -> discord.Member:
        """A function for returning the modified member object after removing roles
        
        (Since member.remove_roles does not return the modified object :/)"""
        new_roles = [discord.Object(id=r.id) for r in member.roles[1:]] # remove @everyone
        for role_id in roles:
            try:
                new_roles.remove(discord.Object(id=role_id))
            except ValueError:
                pass
        
        return await member.edit(roles=new_roles)

    # callback for colour buttons
    async def check_colour_roles(self, interaction: discord.Interaction, role_btn: GenericRoleButton) -> bool:
        regular_role_ids = set(REGULAR_COLOURS)
        premium_role_ids = set(PREMIUM_COLOURS)
        author_roles = set(interaction.user._roles)

        # Heist Leader, Giveaway Manager, Farmer, Double Booster, Partner Manager, Farm Manager, Level 25, $20 Donator, Farm Owner, Daughter
        premium_role_req = {719012715204444181, 790290355631292467, 723035638357819432,
                            855877108055015465, 682698693472026749, 658770981816500234,
                            663162896158556212, 658770586540965911, 794301389769015316,
                            732497481358770186}
        
        # removing premium colours if they don't have the required role(s)
        if (roles_to_remove := author_roles & premium_role_ids) and not (author_roles & premium_role_req):          
            interaction.user = await self.remove_roles(interaction.user, roles_to_remove)
            await interaction.response.send_message(content=f"You're no longer a premium user! To unlock {', '.join(f'<@&{id}>' for id in roles_to_remove)} again, check out our <#898978985608900618> and <#948755871167565824>.", ephemeral=True)
        
        # the above condition may/may not trigger, hence a check is necessary
        send_method = interaction.followup.send if interaction.response.is_done() else interaction.response.send_message

        # denying taking of premium colours
        if not (author_roles & premium_role_req) and role_btn.role_id in premium_role_ids:
            await send_method(content="This is a premium colour! To unlock them, check out our <#898978985608900618> and <#948755871167565824>. (The first 6 colours can be used by you)", ephemeral=True)
            return False

        restricted_role_ids = (regular_role_ids | premium_role_ids) - {role_btn.role_id}
        await RoleHelper.restriction_handler(restricted_role_ids, interaction, "You can only have one color role! {} has been removed.")

        return True

    @commands.command()
    async def send_colour_embed(self, ctx: commands.Context):
        embed = discord.Embed(description="**COLOUR ROLES**\nClick the buttons below to select a colour of your choice.", colour=0x303135)
        await ctx.message.delete()
        await ctx.send(embed=embed, view=self.colour_view)
    

    @commands.command()
    async def send_access_embed(self, ctx: commands.Context):
        embed = RoleHelper.get_embed(ACCESS, description="**CHANNEL ROLES**\nSelect the corresponding buttons to receive access to hidden channels.")
        await ctx.message.delete()
        await ctx.send(embed=embed, view=self.access_view)
    

    # check for bad roles when applying roles
    async def check_ping_roles(self, interaction: discord.Interaction, role_btn: GenericRoleButton) -> bool:
        # Circus animal trying to get Events and Giveaways
        if interaction.user._roles.has(719260653541654608) and role_btn.role_id in (684552219344764934, 672889430171713538):
            await interaction.response.send_message(content="<@&719260653541654608> restricts you from getting this role. DM <@855270214656065556> to appeal.", ephemeral=True)
            return False
        
        # Poor animal trying to get Heist Hipphoes
        if interaction.user._roles.has(761251579381678081) and role_btn.role_id == 684987530118299678:
            await interaction.response.send_message(content="<@&761251579381678081> restricts you from getting this role. DM <@855270214656065556> to appeal.", ephemeral=True)
            return False
        
        # No hype trying to get Hype My Stream
        if interaction.user._roles.has(906203595999944794) and role_btn.role_id == 865796857887981579:
            await interaction.response.send_message(content="<@&906203595999944794> restricts you from getting this role. DM <@855270214656065556> to appeal.", ephemeral=True)
            return False
        
        return True
    
    @commands.command()
    async def send_ping_embed(self, ctx: commands.Context):
        embed = RoleHelper.get_embed(PING, description="**PING ROLES**\nSelect the corresponding buttons to get pinged for various events. ")
        await ctx.message.delete()
        await ctx.send(embed=embed, view=self.ping_view)

    
    # region check
    async def check_region_roles(self, interaction: discord.Interaction, role_btn: GenericRoleButton) -> bool:
        restricted_role_ids = set(REGION) - {role_btn.role_id}
        await RoleHelper.restriction_handler(restricted_role_ids, interaction, "You can only have one region role! {} has been removed.")

        return True 

    @commands.command()
    async def send_region_embed(self, ctx: commands.Context) -> None:
        embed = RoleHelper.get_embed(REGION, description="**REGION ROLES**\nClick the buttons below to show where you're from.")
        await ctx.message.delete()
        await ctx.send(embed=embed, view=self.region_view)


    # age check
    async def check_age_roles(self, interaction: discord.Interaction, role_btn: GenericRoleButton) -> bool:
        restricted_role_ids = set(AGE) - {role_btn.role_id}
        await RoleHelper.restriction_handler(restricted_role_ids, interaction, "You can only have one age group role! {} has been removed.")
        
        return True 

    @commands.command()
    async def send_age_embed(self, ctx: commands.Context) -> None:
        embed = RoleHelper.get_embed(AGE, description="**AGE ROLES**\nClick the buttons below to show what your age is.")
        await ctx.message.delete()
        await ctx.send(embed=embed, view=self.age_view)

    
    async def check_gender_roles(self, interaction: discord.Interaction, role_btn: GenericRoleButton) -> bool:
        restricted_role_ids = set(GENDER) - {role_btn.role_id}
        await RoleHelper.restriction_handler(restricted_role_ids, interaction, "You can only have one gender role! {} has been removed.")
        
        return True 

    @commands.command()
    async def send_gender_embed(self, ctx: commands.Context) -> None:
        embed = RoleHelper.get_embed(GENDER, description="**GENDER ROLES**\nChoose a role you identify with, feel free to switch anytime!")
        await ctx.message.delete()
        await ctx.send(embed=embed, view=self.gender_view)
        
async def setup(bot):
    await bot.add_cog(SelfRoles(bot))
