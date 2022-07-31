import re
import discord

from datetime import datetime, timedelta
from discord.ext import commands, tasks

time_units = {'s': 'seconds', 'm': 'minutes', 'h': 'hours', 'd': 'days', 'w': 'weeks'}
role_info = {719012723509297153: 2, 719012719399010364: 2, 719315104767672350: 3, 719315341716619294: 3,
             719012715204444181: 4, 719315435601788978: 4, 719012710062358560: 5, 753210431983583302: 2,
             649658625224343554: 2, 732497481358770186: 2, 800799561174089758: 4, 733838986992156752: 2,
             794300647137738762: 2, 794301192359378954: 2, 794301389769015316: 2, 794302939371929622: 2,
             682698693472026749: 100, 658770981816500234: 100, 663162896158556212: 100, 658770586540965911: 100,
             814004142796046408: 100, 855877108055015465: 100, 723035638357819432: 100}


# Level 05 - Level 50 increments 2,2,3,3,4,4,5
# Voter gets 2 extra
# Booster, double booster and quad get 2 extra reminders (sat gets extra 4 because 2x)
# Cash donators get 2 extra each level
# All staff roles get 100 extra (basically unlimited)

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coll = bot.plugin_db.get_partition(self)
        self.reminder_loop.start()

    async def maximum_reminders(self, member):
        count = 3
        for role in member.roles:
            if role.id in role_info:
                count += role_info[role.id]
        return count

    @staticmethod
    def to_seconds(s):
        return int(timedelta(**{
            time_units.get(m.group('unit').lower(), 'seconds'): int(m.group('val'))
            for m in re.finditer(r'(?P<val>\d+)(?P<unit>[smhdwy]?)', s, flags=re.I)
        }).total_seconds())

    @commands.command(aliases=['rm'])
    async def remind(self, ctx, time, *, message):
        """Reminds you of something in the future."""
        try:
            text = time
            seconds = sum(
                int(num) *
                {'y': 60 * 60 * 24 * 365, 'w': 60 * 60 * 24 * 7, 'd': 60 * 60 * 24, 'h': 60 * 60, 'm': 60, 's': 1,
                 ' ': 1}[weight if weight else 's'] for num, weight in
                re.findall(r'(\d+)\s?([mshdwy])?', text))
            if seconds < 10:
                await ctx.message.reply('I can\'t remind you under 10 seconds. Maybe improve your memory?')
                return BaseException
            count = await self.maximum_reminders(ctx.author)
            check = await self.coll.count_documents({'user_id': ctx.author.id})
            if check >= count:
                return await ctx.message.reply(f'You can only have {count} reminders at a time. Look at '
                                               f'<#898978985608900618> or <#948755871167565824> to increase this '
                                               f'number!')
            reminder = {"user_id": ctx.author.id, "message": message,
                        "time": datetime.utcnow() + timedelta(seconds=seconds), "msg_link": ctx.message.jump_url}
            await self.coll.insert_one(reminder)
            await ctx.message.reply("Reminder set. You will be dm\'d once it\'s time.")
            if self.reminder_loop.is_running():
                self.reminder_loop.restart()
            else:
                self.reminder_loop.start()
        except ValueError:
            await ctx.message.reply('Invalid time format. Try `??remind 1h30m Hello!`')

    @commands.command(aliases=['rms'])
    async def reminders(self, ctx):
        """Shows all your reminders."""
        reminders = await self.coll.find({"user_id": ctx.author.id}).to_list(None)
        if not reminders:
            await ctx.reply('You have no reminders.')
            return
        embed = discord.Embed(title=f"**{ctx.author.name} Reminders**", description="", color=0x10ea64)
        for x in reminders:
            tim = x["time"]
            timestamp = round(datetime.timestamp(tim))
            embed.description += f'<t:{timestamp}:f> - [{x["message"]}]({x["msg_link"]}) \n'
        max = await self.maximum_reminders(ctx.author)
        used = await self.coll.count_documents({"user_id": ctx.author.id})
        embed.set_footer(text=f"You have {used}/{max} reminders.")
        await ctx.message.reply(embed=embed)

    @commands.command(aliases=['crm'])
    async def clearreminders(self, ctx):
        """Clears all your reminders."""
        await self.coll.delete_many({"user_id": ctx.author.id})
        await ctx.message.reply('All reminders cleared.')

    @tasks.loop()
    async def reminder_loop(self):
        now = datetime.utcnow()
        reminders = await self.coll.find({"time": {"$lte": now}}).to_list(None)
        if not reminders:
            fetch = await self.coll.find().sort('time', 1).to_list(1)
            if fetch:
                for x in fetch:
                    if x['time'] > now:
                        next_reminder = x['time']
                        return await discord.utils.sleep_until(next_reminder)
        for reminder in reminders:
            try:
                user = self.bot.get_user(reminder['user_id'])
                link = reminder['msg_link']
                embed = discord.Embed(title=f"**Reminder!**",
                                      description=f"You asked to be reminded of \"{reminder['message']}\" [here]({link})",
                                      color=0x10ea64)
                await user.send(embed=embed)
                await self.coll.delete_one({"_id": reminder["_id"]})
                fetch = await self.coll.find().sort('time', 1).to_list(1)
                for x in fetch:
                    if x['time'] > now:
                        next_reminder = x['time']
                        return await discord.utils.sleep_until(next_reminder)
            except Exception as e:
                print(e)


async def setup(bot):
    await bot.add_cog(Reminders(bot))
