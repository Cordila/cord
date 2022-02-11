import discord
from discord import Embed
from discord.ext import commands
from dislash import slash_commands, ActionRow, Button, ButtonStyle, MessageInteraction
from itertools import islice
from core import checks
from core.models import PermissionLevel



# name: (id, emoji)
REGULAR_COLOUR_ROLES: dict[str, tuple[int, str]] = {
    "Cat": (669807217444126731, "<:Cat:938660093124292618>"),
    "Dog": (659498316991692832, "<:Dog:938660094042857502>"),
    "Chicken": (658771095167565834, "<:Chicken:938660093619236914>"),
    "Pig": (658771078075908136, "<:Pig:938660094776852490>"),
    "Cow": (658771090792906812, "<:Cow:938660094592294912>"),
    "Random": (766382104539693066, "<a:Random:938826714820255765>"),
}

PREMIUM_COLOUR_ROLES: dict[str, tuple[int, str]] = {
    "Duck": (658787907091300381, "<:Duck:938660094856544256>"),
    "Goose": (671225083020312587, "<:Goose:938660094541967391>"),
    "Bee": (670306986742644798, "<:Bee:938660094340657152>"),
    "Turkey": (820406630004686848, "<:Turkey:938660094239973446>"),
    "Opossum": (658771088704274438, "<:Opossum:938660094428725248>"),
    "Bunny": (658771071050317844, "<:Bunny:938660094147715092>"),
    "Sheep": (670206078742560768, "<:Sheep:938660093715677214>"),
    "Donkey": (820405761413742619, "<:Donkey:938660094034460762>"),
    "Horse": (658771086422573067, "<:Horse:938660094739103754>"),
    "Zebu": (820406409308405790, "<:Zebu:938660094349037598>"),
    "Raccoon": (820406441138454592, "<:Raccoon:938660094613274654>"),
    "Deer": (820406476379258921, "<:Deer:938660094567153755>"),
    "Frog": (820406552816648262, "<:Frog:938660094818795570>"),
    "Fox": (820406606595751976, "<:Fox:938660094147715093>"),
    "Monkey": (820406515063062588, "<:Monkey:938660093849911306>"),
    "Turtle": (700056188859056261, "<:Turtle:938660095150133358>"),
    "Owl": (820406654137794560, "<:Owl:938660095355662356>"),
    "Wolf": (820406679996596244, "<:Wolf:938660094709751818>"),
    "Moose": (820406719209144332, "<:Moose:938660095271780382>"),
}

ACCESS_ROLES: dict[str, tuple[int, str]] = {
    "├── Dank Access──┤": (680115778967699517, "<:dankmemeraccess:939734546147078144>"),
    "├──Pokémon Access─┤": (680115782645973003, "<:pokemonaccess:939738001083347005>"),
    "├── Anime Access──┤": (791439539854901248, "<:animeaccess:939738555364827156>"),
}

PING_ROLES: dict[str, tuple[int, str]] = {
    "● Nitro Giveaway ●": (800660323203022868, "<a:giveaway_blob:939746793225343068>"),
    "● • Giveawayss • ●": (672889430171713538, "<a:giveaway_blob:830768052156104705>"),
    "● • Livestreams • ●": (864637855245795330, "<:status_streaming:939746824187682826>"),
    "● • Event Time! • ●": (684552219344764934, "<:hypesquad_events:939746866294313002>"),
    "● • Mafia Time! • ●": (713898461606707273, "<:mafia:939746925400457307>"),
    "● • Song Contest • ●": (710184003684270231, "<a:2musicvibe:939746897671880794>"),
    "● • Partnership • ●": (793454145897758742, "<a:PartnerShine:939746957918875660>"),
    "● • Farm Medic • ●": (722634660068327474, "<:DeadChat:939746982866608208>"),
    "● • • Lottery • • ●": (732949595633614938, "<:winninglotteryticket:939747030560047104>"),
    "● Friendly Heist ●": (750908803704160268, "💰"),
    "● Daily Question ●": (872546624461738035, "❓"),
    "● Heist Hipphoes ●": (684987530118299678, "<a:fh_pepeheist:939747192451772486>"),
    "● Hype My Stream! ●": (865796857887981579, "<:streaming:939747138030669834>"),
}

REGION_ROLES: dict[str, tuple[int, str]] = {
    "America": (680530862567325894, "<:weed:669828130252259338>"),
    "Asia": (680530901096202340, "<:doge:940947519578472489>"),
    "Europe": (680530881932296202, "<:uwu_nice:940947412875378728>"),
    "Oceania": (680530932901609581, "<a:farm_xhEvilElmo:676545857406894080>"),
    "Middle East": (680530891923390505, "<a:farm_pepeFeelsWeirdMan:673745528819023923>"),
}

AGE_ROLES: dict[str, tuple[int, str]] = {
    "13-17": (672692198176981012 ,"<:farm_vBeanieBaby:672695247595110440>"),
    "18-21": (672693091076931595 ,"<:farm_xdyeet:669762759097057299>"),
    "22-25": (672693107711672330 ,"<:farm_xhricardo:883763285801992224>"),
    "25+": (672693112518475777 ,"<:farm_vHAAA:669780097322188800>"),
}

GENDER_ROLES: dict[str, tuple[int, str]] = {
    "Male": (672687526766575616, "<:farm_3Male:685927852406734884>"),
    "Female": (672688052724039722, "<:farm_3Female:685928377726533669>"),
    "Gender is a social construct": (672688231736672266, "<a:lotsahearts:669780082050596889>"),
}

# role_ids needed for restrictive adding (only one from each category at any one time)
RESRICTIVE_ROLES: dict[str, set[int]] = {
    "colour_roles": set(v[0] for v in REGULAR_COLOUR_ROLES.values()) | set(v[0] for v in PREMIUM_COLOUR_ROLES.values()),
    "region_roles": set(v[0] for v in REGION_ROLES.values()),
    "age_roles": set(v[0] for v in AGE_ROLES.values()),
    "gender_roles": set(v[0] for v in GENDER_ROLES.values()),
}

# The number of hair spaces each character is (approximately)
# used for calculating paddings for strings within buttons
OFFSET = {"a": 6, "b": 7, "c": 6, "d": 7, "e": 6, "f": 3, "g": 6, "h": 7, "i": 3, "j": 3, "k": 6, "l": 3,
          "m": 11, "n": 7, "o": 7, "p": 7, "q": 7, "r": 4, "s": 5, "t": 4, "u": 7, "v": 6, "w": 9, "x": 6,
          "y": 6, "z": 5, "A": 9, "B": 7, "C": 8, "D": 9, "E": 7, "F": 6, "G": 9, "H": 9, "I": 3, "J": 5,
          "K": 8, "L": 6, "M": 12, "N": 9, "O": 9, "P": 7, "Q": 9, "R": 7, "S": 7, "T": 7, "U": 9, "V": 9,
          "W": 13, "X": 8, "Y": 8, "Z": 7, "1": 4, "2": 7, "3": 7, "4": 7, "5": 7, "6": 7, "7": 7, "8": 7, 
          "9": 7, "0": 8, "-": 5, "+": 7,  " ": 3, "é": 6, "●": 7, "•": 5, "├": 9, "┤": 9, "─": 9, "!": 3, }

class SelfRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not hasattr(self.bot, "inter_client"):
            slash_commands.InteractionClient(self.bot)
        
    def calculate_max_padding(self, roles: dict[str, tuple[int, str]]) -> int:
        # calculates the padding length with hair spaces
        max_width = max(sum(OFFSET[c] for c in role_name) for role_name in roles)

        return max_width
    
    def pad_string(self, string: str, max_padding: int) -> str:
        width = sum(OFFSET[c] for c in string)
        return string + "\u200a" * (max_padding - width)

    def get_components(self, roles: dict[str, tuple[int, str]], max_items_per_row: int, role_type: str) -> list[ActionRow]:
        """This is the main function for getting components from a role dictionary."""
        components = []
        # splits the roles into lists of length max_items_per_row each
        split_roles = [islice(roles, x, x+max_items_per_row) for x in range(0, len(roles), max_items_per_row)]

        # calculate the maximum width that the roles would have
        padding = self.calculate_max_padding(roles)

        for r in split_roles:
            row = ActionRow()

            for role_name in r:
                role_id, emoji = roles[role_name]

                row.add_button(
                    style=ButtonStyle.blurple,
                    label= self.pad_string(role_name, padding),
                    custom_id=f"update_self_role:{role_type}:{role_id}",
                    emoji=emoji
                )
            
            components.append(row)
        
        return components
    
    @commands.Cog.listener("on_button_click")
    async def get_roles(self, inter: MessageInteraction):
        """This is the listener mainly responsible for setting up ephemeral
        role buttons.
        
        Buttons who call this listener should have their custom_id in the form of
        `self_roles:<role_type>`
        
        `<role_type>` allows for this listener to pass it onto get_components, where it passes it
        into the buttons

        Currenly used by colour, ping and access embeds.
        """

        if not inter.component.custom_id.startswith("self_roles"):
            return
        
        _, role_type = inter.component.custom_id.split(":")

        # the default is 5, but can be changed
        max_items_per_row = 5

        if role_type == "colour_roles":
            available_roles = REGULAR_COLOUR_ROLES.copy()

            # Heist Leader, Giveaway Manager, Farmer, Double Booster, Partner Manager, Farm Manager, Level 25, $20 Donator, Farm Owner, Daughter
            if bool(set(inter.author._roles) & {719012715204444181, 790290355631292467, 723035638357819432,
                                                855877108055015465, 682698693472026749, 658770981816500234,
                                                663162896158556212, 658770586540965911, 794301389769015316,
                                                732497481358770186}):
                # we add the premium colour roles
                available_roles.update(PREMIUM_COLOUR_ROLES)
        
        if role_type == "access_roles":
            available_roles = ACCESS_ROLES.copy()

        if role_type == "ping_roles":
            available_roles = PING_ROLES.copy()
            max_items_per_row = 4

        # we get the components we need based on the roles and items per row
        components = self.get_components(available_roles, max_items_per_row, role_type)

        await inter.create_response("Which roles do you want to add/remove?", components=components, ephemeral=True)

    @commands.Cog.listener("on_button_click")
    async def update_roles(self, inter: MessageInteraction):
        """This is the main listener responsible for addition/removal of roles
        Buttons which call this listener should have their custom_id in the form of:
        `update_self_role:<role_type>:<role_id>`
        
        `<role_type>` allows for this listener to differentiate between categories that 
        do not allow more than one role on that member.
        
        This listener also disallows people with certain roles to get certain roles."""

        if not inter.component.custom_id.startswith("update_self_role"):
            return
        
        _, role_type, role_id = inter.component.custom_id.split(":")
        role_id = int(role_id)

        # Circus animal
        # giveaways, event time
        if role_id in (672889430171713538, 684552219344764934) and inter.author._roles.has(719260653541654608):
            return await inter.create_response("You have <@&719260653541654608> and can't take this role!\nDM me to appeal!", ephemeral=True)

        # Poor animal
        if role_id == 684987530118299678 and inter.author._roles.has(761251579381678081):
            return await inter.create_response("You have <@&761251579381678081> and can't take this role!\nDM me to appeal!", ephemeral=True)
        
        # No hype for you!
        if role_id == 865796857887981579 and inter.author._roles.has(906203595999944794):
            return await inter.create_response("You have <@&906203595999944794> and can't take this role!\nDM me to appeal!", ephemeral=True)
        
        resp = ""

        if role_type in ("colour_roles", "region_roles", "age_roles", "gender_roles"):
            filter_ids = RESRICTIVE_ROLES[role_type]

            conflicting = set(inter.author._roles) & filter_ids

            if conflicting:
                await inter.author.remove_roles(*[discord.Object(id) for id in conflicting])
                resp += "Removed " + ", ".join(f"<@&{id}>" for id in conflicting) + "."

        if inter.author._roles.has(role_id):
            await inter.author.remove_roles(discord.Object(role_id))
            resp += f"Removed <@&{role_id}>."
        
        # does not have the role
        else:
            await inter.author.add_roles(discord.Object(role_id))
            resp += f"Added <@&{role_id}>."
        
        await inter.create_response(resp, ephemeral=True)


    # colour, access, ping roles
    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def send_colour_embed(self, ctx: commands.Context):
        row = ActionRow(Button( style=ButtonStyle.green, label="Click me!", custom_id="self_roles:colour_roles") )

        colour_embed = Embed(title="Get your colour roles here!", description="Click the button below to choose colour roles", color=0x90ee90)

        await ctx.message.delete()
        await ctx.send(embed=colour_embed, components=[row])

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def send_access_embed(self, ctx: commands.Context):
        row = ActionRow( Button(style=ButtonStyle.green, label="Click me!", custom_id="self_roles:access_roles") )

        access_embed = Embed(title="Get your colour roles here!", description="Click the button below to choose access roles", colour=0x90ee90)

        await ctx.message.delete()
        await ctx.send(embed=access_embed, components=[row])

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def send_ping_embed(self, ctx: commands.Context):
        row = ActionRow( Button(style=ButtonStyle.green, label="Click me!", custom_id="self_roles:ping_roles") )

        ping_embed = Embed(title="Get your colour roles here!", description="Click the button below to choose ping roles", colour=0x90ee90)

        await ctx.message.delete()
        await ctx.send(embed=ping_embed, components=[row])


    # fun roles
    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def send_region_embed(self, ctx: commands.Context):
        components = self.get_components(REGION_ROLES, 5, "region_roles")

        region_embed = Embed(title="Choose one, switch anytime!", description="Get your region roles here!", colour=0x90ee90)

        await ctx.message.delete()
        await ctx.send(embed=region_embed, components=components)

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def send_age_embed(self, ctx: commands.Context):
        components = self.get_components(AGE_ROLES, 5, "age_roles")

        age_embed = Embed(title="Choose one, switch anytime!", description="Get your age roles here!", colour=0x90ee90)

        await ctx.message.delete()
        await ctx.send(embed=age_embed, components=components)
    
    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def send_gender_embed(self, ctx: commands.Context):
        components = self.get_components(GENDER_ROLES, 5, "gender_roles")

        gender_embed = Embed(title="Choose one, switch anytime!", description="Get your gender roles here!", color=0x90ee90)

        await ctx.message.delete()
        await ctx.send(embed=gender_embed, components=components)


    # specific roles
    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def send_mafia_embed(self, ctx: commands.Context):
        # passing in _ as the role_type since it doesn't matter
        row = ActionRow(Button(style=ButtonStyle.green, label="● • Mafia Time! • ●", custom_id="update_self_role:_:713898461606707273"))


        mafia_embed = Embed(title="Mafia", description="Click the button below to get the <@&713898461606707273> role so you can get notifications for games and access the <#756552586248585368> and <#756566417456889965> channels", colour=0x90ee90)

        await ctx.message.delete()
        await ctx.send(embed=mafia_embed, components=[row])
        
    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def send_dank_embed(self, ctx: commands.Context):
        # passing in _ as the role_type since it doesn't matter
        row = ActionRow(Button(style=ButtonStyle.green, label="├── Dank Access──┤", custom_id="update_self_role:_:680115778967699517"))


        dank_embed = Embed(title="Having trouble viewing the dank memer channels below?", description="Click the button below to get the <@&680115778967699517> role and gain access to trade/fight and other dank channels", colour=0x90ee90)

        await ctx.message.delete()
        await ctx.send(embed=dank_embed, components=[row])
        
    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def send_pokemon_embed(self, ctx: commands.Context):
        # passing in _ as the role_type since it doesn't matter
        row = ActionRow(Button(style=ButtonStyle.green, label="├──Pokémon Access─┤", custom_id="update_self_role:_:680115782645973003"))


        pokemon_embed = Embed(title="Having trouble seeing all of the pokemon channels in the server?", description="Click the button below to get the <@&680115782645973003> role and gain access to the pokemon channels", colour=0x90ee90)

        await ctx.message.delete()
        await ctx.send(embed=pokemon_embed, components=[row])
        
    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def send_anime_embed(self, ctx: commands.Context):
        # passing in _ as the role_type since it doesn't matter
        row = ActionRow(Button(style=ButtonStyle.green, label="├──Anime Access──┤", custom_id="update_self_role:_:791439539854901248"))


        anime_embed = Embed(title="React for access to the anime bot channels!", description="__**Anime bots:**__ \n  <@722418701852344391> \n <@432610292342587392> \n <@571027211407196161> \n <@646937666251915264> (Level 10 req) \n <@280497242714931202>", colour=0x90ee90)

        await ctx.message.delete()
        await ctx.send(embed=anime_embed, components=[row])
        
    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def send_friendly_embed(self, ctx: commands.Context):
        # passing in _ as the role_type since it doesn't matter
        row = ActionRow(Button(style=ButtonStyle.green, label="├──Friendly Heist Access──┤", custom_id="update_self_role:_:750908803704160268"))


        friendly_heist_embed = Embed(description="<@&750908803704160268> - React to be notified of Friendly Heists both in Bot Farm and partnered servers!", colour=0x90ee90)

        await ctx.message.delete()
        await ctx.send(embed=friendly_heist_embed, components=[row])
        
    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def send_heist_embed(self, ctx: commands.Context):
        # passing in _ as the role_type since it doesn't matter
        row = ActionRow(Button(style=ButtonStyle.green, label="● Heist Hipphoes ●", custom_id="update_self_role:_:684987530118299678"))


        heist_embed = Embed(description="<@&684987530118299678> - React to be notified of **UN**-Friendly Heists that are scouted by members and **__take place in rob/heist enabled servers!__**", colour=0x90ee90)

        await ctx.message.delete()
        await ctx.send(embed=heist_embed, components=[row])
        
    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def send_giveaways_embed(self, ctx: commands.Context):
        # passing in _ as the role_type since it doesn't matter
        row = ActionRow(Button(style=ButtonStyle.green, label="● • Giveawayss • ●", custom_id="update_self_role:_:672889430171713538"))


        giveaways_embed = Embed(title="Giveaways", description="React below to be notified of giveaways including: \n ⇾ Dank Memer Coins \n ⇾ Dank Memer Items \n ⇾ Discord Nitro \n ⇾ More random giveaways! \n <@&672889430171713538>", colour=0x90ee90)

        await ctx.message.delete()
        await ctx.send(embed=giveaways_embed, components=[row])
    
    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def send_events_embed(self, ctx: commands.Context):
        # passing in _ as the role_type since it doesn't matter
        row = ActionRow(Button(style=ButtonStyle.green, label="● • Event Time! • ●", custom_id="update_self_role:_:684552219344764934"))


        event_embed = Embed(title="Events", description="React below to be notified of Events including:\n ⇾ Tea \n ⇾ Bingo \n ⇾ Coin Bombs \n ⇾ Quiplash \n ⇾ Guessing Games \n ⇾ Online Games \n ⇾ Custom Events and More! \n <@&684552219344764934>", colour=0x90ee90)

        await ctx.message.delete()
        await ctx.send(embed=event_embed, components=[row])
        
def setup(bot):
    bot.add_cog(SelfRoles(bot))
