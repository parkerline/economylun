import disnake; from disnake.ext import commands; from disnake import *; from disnake.ui import *;
import time; import re; import asyncio;
from settings.config import *; from settings.db import *; from server.conf.emoji import *; from server.conf.cfg import *


class ManageTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.manage_roles())

    async def manage_roles(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            guild = self.bot.get_guild(BOT["GUILD_ID"])
            role_pair = disnake.utils.get(guild.roles, id=ЛЮБОВНЫЕРУМЫ['роль пары'])
            # Пробегаемся по всем бракам и выдаем роль пары
            async for brak in braki.find({}):
                if brak['пара']['первый'] and brak['пара']['второй']:
                    member_first = guild.get_member(brak['пара']['первый'])
                    member_second = guild.get_member(brak['пара']['второй'])
                    if member_first and not role_pair in member_first.roles:
                        await member_first.add_roles(role_pair)
                    if member_second and not role_pair in member_second.roles:
                        await member_second.add_roles(role_pair)
            for member in role_pair.members:
                brak_exists = await braki.find_one({'$or': [{'пара.первый': member.id}, {'пара.второй': member.id}]})
                if not brak_exists:
                    await member.remove_roles(role_pair)
            await asyncio.sleep(25)
            
def setup(bot):
    bot.add_cog(ManageTask(bot))