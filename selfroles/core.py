import discord
from typing import Callable

class GenericRoleButton(discord.ui.Button): pass # this is to get the line below to work :/
Callback = Callable[[discord.Interaction, GenericRoleButton], bool]
Roles = dict[int, str]

# this is pretty much the meat of what we want
# this is a factory class that returns a button given an emoji, role_id (and custom callback)
class GenericRoleButton(discord.ui.Button):
    def __init__(self, *, emoji: str, role_id: int, callback: Callback = None):
        """Here, a callback that accepts two arguments, the button instance and the interaction will be passed in.
        This function will be called before the role adding/removing will be executed,
        allowing for this function to serve as a restriction.

        This callback has to be asynchronous.

        A boolean of True or False has to be returned indicating if execution should continue"""

        self.role_id = role_id
        super().__init__(emoji=emoji, style=discord.ButtonStyle.grey, custom_id=f"self_roles:toggle_role:{role_id}")

        self._callback = callback

    async def callback(self, interaction: discord.Interaction):
        # here is where the custom callback is called
        # if the return value is False, execution will stop
        if self._callback is not None:
            continue_execution = await self._callback(interaction, self)
            
            if not continue_execution:
                return
        
        # just in case the interaction response has been used
        send_method = interaction.followup.send if interaction.response.is_done() else interaction.response.send_message

        if self.role_id in interaction.user._roles:
            await interaction.user.remove_roles(discord.Object(id=self.role_id))
            return await send_method(content=f"Removed <@&{self.role_id}>!", ephemeral=True)

        await interaction.user.add_roles(discord.Object(id=self.role_id))
        await send_method(content=f"Added <@&{self.role_id}>!", ephemeral=True)

class RoleHelper:
    # this returns an embed which does the emoji -> role mapping
    # for users to see
    @classmethod
    def get_embed(cls, roles: Roles, *, title: str = None, description: str = None) -> discord.Embed:
        embed = discord.Embed(title=title, colour=0x303135)
        
        for role_id, role_emoji in roles.items():
            description += f"\n{role_emoji} ➜ <@&{role_id}>"
        
        embed.description = description

        return embed

    # this returns a view that displays each of the emojis
    @classmethod
    def get_view(cls, roles: Roles, btn_callback: Callback = None) -> discord.ui.View:
        view = discord.ui.View(timeout=None)

        for role_id, role_emoji in roles.items():
            view.add_item(GenericRoleButton(emoji=role_emoji, role_id=role_id, callback=btn_callback))

        return view
    
    # this does the most simple restriction testing, removing roles from the same category
    @classmethod
    async def restriction_handler(cls, restricted_role_ids: set[int], interaction: discord.Interaction, response: str) -> None:
        # response has to be a string with {} to format into
        roles_to_remove = restricted_role_ids & set(interaction.user._roles)

        # just in case the interaction response has been used
        send_method = interaction.followup.send if interaction.response.is_done() else interaction.response.send_message

        if roles_to_remove:
            await interaction.user.remove_roles(*[discord.Object(id=id) for id in roles_to_remove])
            await send_method(content=response.format(", ".join(f'<@&{id}>' for id in roles_to_remove)), ephemeral=True)
