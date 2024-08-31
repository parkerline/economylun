import disnake; from disnake.ext import commands; from disnake import *; from disnake.ui import *;
import time; import re; import asyncio;
from settings.config import *; from settings.db import *; from server.conf.emoji import *; from server.conf.cfg import *; from server.db.dbfunc import *;


class Top(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_online_rank(self, user):
        documents = users.find().sort("профиль.общий онлайн", pymongo.DESCENDING)
        documents = await documents.to_list(None)

        for i, document in enumerate(documents):
            if document['айди'] == user.id:
                return i + 1

        return None
    
    @commands.slash_command(name="top", description="Показывает топ пользователей")
    async def top(self, interaction: disnake.ApplicationCommandInteraction, mode: str = commands.Param(choices=["монетки", "онлайн", "сообщения"])):
        await interaction.response.defer()
        if mode == "монетки":
            user_list = await users.find().sort('профиль.баланс', -1).limit(10).to_list(10)
            description = ""
            for i, user in enumerate(user_list):
                member = interaction.guild.get_member(user['айди'])
                description += f"{i + 1}. {member.mention} - Баланс: {user['профиль']['баланс']} {ЭМОДЗИ['money']}\n"
            embed = disnake.Embed(
                title="Топ 10 пользователей по балансу",
                description=description
            )
        elif mode == "онлайн":
            user_list = await users.find().sort('профиль.общий онлайн', -1).limit(10).to_list(10)
            user_info_list = []

            # Собираем информацию о каждом пользователе
            for user in user_list:
                member = interaction.guild.get_member(user['айди'])
                rank = await self.get_online_rank(member)
                seconds = user['профиль']['общий онлайн']
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                user_info_list.append({
                    'rank': rank,
                    'member_mention': member.mention,
                    'hours': hours,
                    'minutes': minutes
                })

            # Сортируем список пользователей по рангу
            sorted_user_info_list = sorted(user_info_list, key=lambda x: x['rank'])

            # Формируем описание для embed
            description = ""
            for user_info in sorted_user_info_list:
                description += f"**{user_info['rank']}**){user_info['member_mention']} - **{user_info['hours']} час {user_info['minutes']} минут** \n"

            embed = disnake.Embed(
                title="Топ 10 пользователей по общему онлайну",
                description=description
            )
        
        elif mode == "сообщения":
            user_list = await users.find().sort('профиль.сообщений', -1).limit(10).to_list(10)
            description = ""
            for i, user in enumerate(user_list):
                member = interaction.guild.get_member(user['айди'])
                messages_count = user['профиль']['сообщений']
                description += f"{i + 1}. {member.mention} - Сообщений: {messages_count}\n"
            embed = disnake.Embed(
                title="Топ 10 пользователей по количеству сообщений",
                description=description
            )
            
        embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
        embed.set_footer(text="Экономика", icon_url=self.bot.user.display_avatar.url)
        await interaction.edit_original_message(embed=embed)

def setup(bot):
    bot.add_cog(Top(bot))