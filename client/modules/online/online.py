import disnake; from disnake.ext import commands; from disnake import *; from disnake.ui import *;
import time; import re; import asyncio;
from settings.config import *; from settings.db import *; from server.conf.emoji import *; from server.conf.cfg import *


class TaskOnline(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.addbalance())
        self.bot.loop.create_task(self.update_online())
        self.bot.loop.create_task(self.reset_daily_online())
        self.bot.loop.create_task(self.reset_weekly_online())

    async def addbalance(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            guild = self.bot.get_guild(int(BOT['GUILD_ID']))
            if guild is not None:
                for vc in guild.voice_channels:
                    for member in vc.members:
                        user = await users.find_one({'айди': member.id})
                        if user:
                            await users.update_one({'айди': user['айди']}, {'$inc': {'профиль.баланс': 10}})
                            try:
                                #embed = disnake.Embed(
                                    #title="**Начисление монет**",
                                    #description="Вам было начислено 100 монет за нахождение в голосовом канале.",
                                #)
                                #embed.set_thumbnail(url=self.bot.user.display_avatar.url)
                                #await member.send(embed=embed)
                                pass
                            except disnake.Forbidden:
                                pass
            await asyncio.sleep(300)

    async def update_online(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            guild = self.bot.get_guild(BOT["GUILD_ID"])
            if guild is not None:
                for channel in guild.voice_channels:
                    for member in channel.members:
                        user = await users.find_one({'айди': member.id})
                        if user is not None:
                            user['профиль']['общий онлайн'] += 1
                            user['профиль']['онлайн за день'] += 1
                            user['профиль']['онлайн за неделю'] += 1
                            await users.update_one({'айди': member.id}, {'$set': user})
            await asyncio.sleep(1)
            
    '''async def update_online(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            guild = self.bot.get_guild(BOT["GUILD_ID"])
            if guild is not None:
                for channel in guild.voice_channels:
                    # Проверяем, является ли канал модвойсом
                    if channel.id in ОНЛАЙНКАНАЛЫ['модвойсы']:
                        for member in channel.members:
                            user = await users.find_one({'айди': member.id})
                            if user is not None:
                                user['профиль']['общий онлайн'] += 1
                                user['профиль']['онлайн за день'] += 1
                                user['профиль']['онлайн за неделю'] += 1
                                await users.update_one({'айди': member.id}, {'$set': user})
            await asyncio.sleep(1)'''

    async def reset_daily_online(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            now = time.gmtime()
            if now.tm_hour == 0 and now.tm_min == 0:
                await users.update_many({}, {'$set': {'профиль.онлайн за день': 0}})
            await asyncio.sleep(60)

    async def reset_weekly_online(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            now = time.gmtime()
            if now.tm_wday == 0 and now.tm_hour == 0 and now.tm_min == 0:  # Reset at midnight on Monday
                await users.update_many({}, {'$set': {'профиль.онлайн за неделю': 0}})
            await asyncio.sleep(60)


def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours}ч {minutes}мин"

class Online(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="online", description="Посмотреть онлайн участников")
    async def online(self, interaction: disnake.ApplicationCommandInteraction, member: disnake.Member = None):
        await interaction.response.defer()
        if member is None:
            member = interaction.author
        user = await users.find_one({'айди': member.id})
        if user is None:
            await interaction.response.send_message("Вы не зарегистрированы в базе данных", ephemeral=True)
            return
        embed = disnake.Embed(
            title=f"**Онлайн пользователя — {member.display_name}**",
        )
        embed.add_field(name="Общий онлайн", value=f"```{format_time(user['профиль']['общий онлайн'])}```")
        embed.add_field(name="Онлайн за день", value=f"```{format_time(user['профиль']['онлайн за день'])}```")
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
        embed.set_footer(text=f"Онлайн", icon_url=self.bot.user.display_avatar.url)
        message = await interaction.edit_original_message(embed=embed)

def setup(bot):
    bot.add_cog(TaskOnline(bot))
    bot.add_cog(Online(bot))
