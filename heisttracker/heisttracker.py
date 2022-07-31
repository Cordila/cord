import asyncio
import re
from typing import Optional

import discord
from discord.ext import commands

RESULTS_REGEX = re.compile(r"```(?:diff)?\n(?:[+#].+⏣ \d{0,3}(?:,\d{3})*.+\n?|- .+ died RIP\n)*\n*```")
LEADER_REGEX = re.compile(r"led.+<@!?(\d{17,19})>", flags=re.I)
SCOUTER_REGEX = re.compile(r"scout.+<@!?(\d{17,19})>", flags=re.I)
AMOUNT_REGEX = re.compile(r"Amazing job everybody,.+?([1-9]\d{0,2}(?:,\d{3})*).*")
BACKUP_AMOUNT_REGEX = re.compile(r"\+.+⏣ ([1-9]\d{0,2}(?:,\d{3})*)")


class HeistTracker(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.coll = bot.plugin_db.get_partition(self)

    def check_valid_results(self, content: str) -> bool:
        return bool(RESULTS_REGEX.search(content))

    def get_id(self, person: str, content: str) -> Optional[int]:
        if person == "leader":
            regex = LEADER_REGEX
        if person == "scouter":
            regex = SCOUTER_REGEX

        match = regex.search(content)

        if match is None:
            return None

        return int(match.group(1))

    def get_amount(self, content: str) -> int:
        match = AMOUNT_REGEX.search(content)

        if match is not None:
            return int(match.group(1).replace(",", ""))

        # if "Amazing job everyone, ..." isn't placed into the
        # message, we tally everyone's earnings through the codeblock.
        return content.count("\n+") * int(BACKUP_AMOUNT_REGEX.search(content).group(1).replace(",", ""))

    async def update_db(self, leader_id: int, scouter_id: int, amount: int) -> None:
        # updates database with values using pymongo
        leadercheck = await self.coll.find_one({"user_id": leader_id})
        if leadercheck is None:
            await self.coll.insert_one({"user_id": leader_id, "led_maximum": amount, "scouted_maximum": 0,
                                        "led_amount": amount, "scouted_amount": 0, "led_count": 1,
                                        "scouted_count": 0})
        else:
            led_maximum = leadercheck["led_maximum"]
            old_led_amount = leadercheck["led_amount"]
            new_led_amount = old_led_amount + amount
            old_led_count = leadercheck["led_count"]
            new_led_count = old_led_count + 1
            if led_maximum < amount:
                await self.coll.update_one({"user_id": leader_id},
                                           {"$set": {"led_maximum": amount, "led_amount": new_led_amount,
                                                     "led_count": new_led_count}})
            await self.coll.update_one({"user_id": leader_id},
                                       {"$set": {"led_amount": new_led_amount, "led_count": new_led_count}})

        scoutercheck = await self.coll.find_one({"user_id": scouter_id})
        if scoutercheck is None:
            await self.coll.insert_one({"user_id": scouter_id, "led_maximum": 0, "scouted_maximum": amount,
                                        "led_amount": 0, "scouted_amount": amount, "led_count": 0,
                                        "scouted_count": 1})
        else:
            scouted_maximum = scoutercheck["scouted_maximum"]
            old_scouted_amount = scoutercheck["scouted_amount"]
            new_scouted_amount = old_scouted_amount + amount
            old_scouted_count = scoutercheck["scouted_count"]
            new_scouted_count = old_scouted_count + 1
            if scouted_maximum < amount:
                await self.coll.update_one({"user_id": scouter_id},
                                           {"$set": {"scouted_maximum": amount, "scouted_amount": new_scouted_amount,
                                                     "scouted_count": new_scouted_count}})
            await self.coll.update_one({"user_id": scouter_id},
                                       {"$set": {"scouted_amount": new_scouted_amount,
                                                 "scouted_count": new_scouted_count}})

    @commands.Cog.listener("on_message")
    async def recv_heist_msg(self, message: discord.Message):
        # trophy room
        if message.channel.id != 669866611313999882:
            return

        # we do this just in case the bot auto-deletes the heist message
        # if there's sensitive words in the message
        await asyncio.sleep(5)
        try:
            await message.channel.fetch_message(message.id)
        except discord.NotFound:
            # if the message has been deleted, ignore
            return

        content = message.content

        if not self.check_valid_results(content):
            return

        leader_id = self.get_id("leader", content)
        scouter_id = self.get_id("scouter", content)

        # either one of the ids are missing
        if not all((leader_id, scouter_id)):
            return

        amount = self.get_amount(content)

        await self.update_db(leader_id, scouter_id, amount)

    @commands.command(aliases=["hs", "heiststatistics", "heiststat"])
    @commands.has_any_role(682698693472026749, 658770981816500234, 663162896158556212, 658770586540965911,
                           814004142796046408, 855877108055015465, 723035638357819432)
    async def heiststats(self, ctx: commands.Context, user: discord.Member = None):
        target = user or ctx.author
        user_id = target.id

        res = await self.coll.find_one({"user_id": user_id})

        if res is None:
            return await ctx.send(f"{target} does not have any unfriendly heist statistics")

        embed = discord.Embed(title=f"{target}'s unfriendly heist statistics!", colour=0x303135)

        embed.description = (
            f"Number of heists led: **{res['led_count']:,}**\n"
            f"Total amount led: **⏣ {res['led_amount']:,}**\n"
            f"Largest amount led in one heist: **⏣ {res['led_maximum']:,}**\n"
            "\n"
            f"Number of heists scouted: **{res['scouted_count']:,}**\n"
            f"Total amount scouted: **⏣ {res['scouted_amount']:,}**\n"
            f"Largest amount scouted in one heist: **⏣ {res['scouted_maximum']:,}**\n"
        )

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(HeistTracker(bot))
