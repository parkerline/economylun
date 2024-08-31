import disnake; from disnake.ext import commands; from disnake import *; from disnake.ui import *;
import time; import re; import asyncio;
from settings.config import *; from settings.db import *; from server.conf.emoji import *; from server.conf.cfg import *


class Message(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == ОНЛАЙНКАНАЛЫ['чат']:
            user_data = await db.users.find_one({"айди": message.author.id})
            if user_data:
                await db.users.update_one(
                    {"айди": message.author.id},
                    {"$inc": {"профиль.сообщений": 1}}
                )

def setup(bot):
    bot.add_cog(Message(bot))