import disnake; from disnake.ext import commands; from disnake import *; from disnake.ui import *;
import time; import re;
from settings.config import *; from settings.db import *; from server.conf.emoji import *; from server.conf.cfg import *


class Timely(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="timely", description="Получить ежедневный бонус")
    async def timely(self, interaction: disnake.ApplicationCommandInteraction):
        await interaction.response.defer()
        user = await users.find_one({'айди': interaction.author.id})
        if user is None:
            await interaction.followup.send("Вы не зарегистрированы в базе данных", ephemeral=True)
            return
        if user['последний бонус'] is not None:
            if time.time() - user['последний бонус'] < 43200:
                embed = disnake.Embed(
                    title="**Ежедневный бонус**",
                    description=f"Вы уже получили бонус сегодня",
                )
                embed.add_field(name="Время до следующего бонуса", value=f"```{int(43200 - (time.time() - user['последний бонус'])) // 3600} часов {int(43200 - (time.time() - user['последний бонус'])) % 3600 // 60} минут```")
                embed.set_thumbnail(url=interaction.author.display_avatar.url)
                embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
                embed.set_footer(text=f"Бонус", icon_url=self.bot.user.display_avatar.url)
                await interaction.edit_original_message(embed=embed)
                return
        await users.update_one({'айди': interaction.author.id}, {'$set': {'последний бонус': time.time()}})
        await users.update_one({'айди': interaction.author.id}, {'$inc': {'профиль.баланс': 100}})
        embed = disnake.Embed(
            title="**Ежедневный бонус**",
            description=f"Вы получили 100 {ЭМОДЗИ['money']}",
        )
        embed.add_field(name="Новый баланс", value=f"```{user['профиль']['баланс'] + 100}```")
        embed.set_thumbnail(url=interaction.author.display_avatar.url)
        embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
        embed.set_footer(text=f"Бонус", icon_url=self.bot.user.display_avatar.url)
        await interaction.edit_original_message(embed=embed)

def setup(bot):
    bot.add_cog(Timely(bot))