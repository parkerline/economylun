import disnake; from disnake.ext import commands; from settings.config import *;
import time
import pymongo; import asyncio; from motor.motor_asyncio import AsyncIOMotorClient; from settings.db import *;

class DBSTARTER(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild = bot.get_guild(BOT["GUILD_ID"])
        self.bot.loop.create_task(self.dbstarter())

    async def dbstarter(self):
        while True:
            self.bot.loop.create_task(self.asd())
            self.bot.loop.create_task(self.loveroomidcheck())
            await asyncio.sleep(10)

    async def asd(self):
        all_marriages = await braki.find({}).to_list(length=None)
        for marriage in all_marriages:
            first_user = await users.find_one({'айди': marriage['пара']['первый']})
            second_user = await users.find_one({'айди': marriage['пара']['второй']})
            if not first_user or not second_user:
                print(f'First user: {first_user}')
                print(f'Second user: {second_user}')
                await braki.delete_one({'_id': marriage['_id']})
                print('Удален брак из-за отсутствия одного из участников') 

    async def loveroomidcheck(self):
        all_loverooms = await braki.find({'лав рума': True}).to_list(length=None)
        for loveroom in all_loverooms:
            room_id = loveroom['айди румы']
            if room_id is None:  # проверка на None
                continue  # пропустить итерацию, если room_id равен None
            room = self.bot.get_channel(room_id)
            if room is None:
                await braki.update_one({'_id': loveroom['_id']}, {'$set': {'айди румы': None}})
                print(f'Удален ID канала из-за его отсутствия на сервере: {room_id}')

def setup(bot):
    bot.add_cog(DBSTARTER(bot))