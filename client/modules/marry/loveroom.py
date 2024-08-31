import disnake; from disnake.ext import commands; from disnake import *; from disnake.ui import *;
import time; import re; import asyncio;
from settings.config import *; from settings.db import *; from server.conf.emoji import *; from server.conf.cfg import *

class Loveroom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_check_tasks = {}
        self.online_time_tasks = {}
        self.roomsettings = {}
        self.voice_channel_cleaner_task = self.bot.loop.create_task(self.check_and_clean_empty_voice_channels())

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel and after.channel.id == ЛЮБОВНЫЕРУМЫ['войс']:
                brak_info = await braki.find_one({'пара.первый': member.id}) or await braki.find_one({'пара.второй': member.id})
                if not brak_info or not brak_info.get('лав рума', False):
                    await member.move_to(None)
                    return 
                second_member_id = brak_info['пара']['второй'] if brak_info['пара']['первый'] == member.id else brak_info['пара']['первый']
                second_member = member.guild.get_member(second_member_id)
                if brak_info['айди румы']:
                    room = self.bot.get_channel(brak_info['айди румы'])
                else:
                    category = self.bot.get_channel(ЛЮБОВНЫЕРУМЫ['категория создания войса'])
                    room_name = brak_info['название любовной румы'] if brak_info['название любовной румы'] != 'не установлено' else f"{member.name} ♥ {second_member.name if second_member else 'Unknown'}"
                    overwrites = {
                        member.guild.default_role: disnake.PermissionOverwrite(view_channel=True, connect=False),
                        member: disnake.PermissionOverwrite(connect=True),
                        second_member: disnake.PermissionOverwrite(connect=True) if second_member else None
                    }
                    for role_id in РУМЫ['запрет']:
                        role = member.guild.get_role(role_id)
                        if role:
                            overwrites[role] = disnake.PermissionOverwrite(view_channel=False, connect=False)
                    for role_id in РУМЫ['мальчик-девочка']:
                        role = member.guild.get_role(role_id)
                        if role:
                            overwrites[role] = disnake.PermissionOverwrite(view_channel=True, connect=False)
                    room = await category.create_voice_channel(name=room_name, overwrites=overwrites)
                    await braki.update_one({'_id': brak_info['_id']}, {'$set': {'айди румы': room.id}})
                    self.voice_check_tasks[room.id] = self.bot.loop.create_task(self.check_voice_room_empty(room))
                await member.move_to(room)

                if room.id not in self.online_time_tasks:
                    self.online_time_tasks[room.id] = self.bot.loop.create_task(self.increase_online_time(brak_info, room))
    
    async def increase_online_time(self, brak_info, room):
        while True:
            await asyncio.sleep(1)
            if len(room.members) == 2:
                await braki.update_one({'_id': brak_info['_id']}, {'$inc': {'онлайн пары': 1}})

    async def check_voice_room_empty(self, room):
        while True:
            await asyncio.sleep(5)
            if not room.members:
                await braki.update_one({'айди румы': room.id}, {'$set': {'айди румы': None}})
                await room.delete()
                self.voice_check_tasks.pop(room.id, None)
                if room.id in self.online_time_tasks:
                    self.online_time_tasks[room.id].cancel()
                    self.online_time_tasks.pop(room.id, None)
                break
            
    async def check_and_clean_empty_voice_channels(self):
        category_id = ЛЮБОВНЫЕРУМЫ['категория создания войса']
        exclude_channel_id = ЛЮБОВНЫЕРУМЫ['войс']
        category = self.bot.get_channel(category_id)
        
        if not category or not isinstance(category, disnake.CategoryChannel):
            return
        
        while True:
            await asyncio.sleep(3)
            for channel in category.voice_channels:
                if channel.id != exclude_channel_id and len(channel.members) == 0:
                    db_brak = await braki.find_one({'айди румы': channel.id})
                    if db_brak:
                        await braki.update_one({'айди румы': channel.id}, {'$set': {'айди румы': None}})
                    await channel.delete()

    def cog_unload(self):
        self.voice_channel_cleaner_task.cancel()

def setup(bot):
    bot.add_cog(Loveroom(bot))