import disnake; from disnake.ext import commands; from disnake import *; from disnake.ui import *;
import time; import random;
from settings.config import *; from settings.db import *; from server.conf.emoji import *


class RepView(disnake.ui.View):
    def __init__(self, bot, user, author, message):
        super().__init__(timeout=60)
        self.bot = bot
        self.user = user
        self.author = author
        self.message = message

    @disnake.ui.button(label='Повысить', style=disnake.ButtonStyle.gray)
    async def up_rep(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        user_data = await users.find_one({"айди": self.user.id})
        if user_data is None:
            await interaction.response.send_message("Пользователь не найден в базе данных", ephemeral=True)
            return
        await users.update_one({"айди": self.user.id}, {"$inc": {"профиль.репутация": 1}})
        await users.update_one({"айди": self.author.id}, {"$set": {"профиль.последнее повышение репутации": time.time()}})
        embed = disnake.Embed(
            title='Репутация',
            description=f"Вы успешно повысили репутацию пользователю {self.user.mention}",
        )
        embed.set_thumbnail(url=self.user.display_avatar.url)
        embed.set_author(name=self.author.display_name, icon_url=self.author.display_avatar.url)
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)
        await self.message.edit(embed=embed, view=None)

    @disnake.ui.button(label='Понизить', style=disnake.ButtonStyle.gray)
    async def lower_rep(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        user_data = await users.find_one({"айди": self.user.id})
        if user_data is None:
            await interaction.response.send_message("Пользователь не найден в базе данных", ephemeral=True)
            return
        await users.update_one({"айди": self.user.id}, {"$inc": {"профиль.репутация": -1}})
        await users.update_one({"айди": self.author.id}, {"$set": {"профиль.последнее повышение репутации": time.time()}})
        embed = disnake.Embed(
            title='Репутация',
            description=f"Вы успешно понизили репутацию пользователю {self.user.mention}",
        )
        embed.set_thumbnail(url=self.user.display_avatar.url)
        embed.set_author(name=self.author.display_name, icon_url=self.author.display_avatar.url)
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)
        await self.message.edit(embed=embed, view=None)

class Rep(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.slash_command(name="rep", description="Повысить/понизить репутацию пользователю")
    async def rep(self, interaction: disnake.ApplicationCommandInteraction, user: disnake.Member):
        await interaction.response.defer()
        if user.bot:
            embed = disnake.Embed(
                title='Репутация',
                description="Вы не можете повысить/понизить репутацию боту",
            )
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
            embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)
            await interaction.edit_original_message(embed=embed)
            return
        if user.id == interaction.author.id:
            embed = disnake.Embed(
                title='Репутация',
                description="Вы не можете повысить/понизить свою репутацию",
            )
            embed.set_thumbnail(url=interaction.author.display_avatar.url)
            embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
            embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)
            await interaction.edit_original_message(embed=embed)
            return
        user_data = await users.find_one({"айди": user.id})
        author_data = await users.find_one({"айди": interaction.author.id})
        if user_data is None:
            await interaction.response.send_message("Пользователь не найден в базе данных", ephemeral=True)
            return
        if author_data['профиль']['последнее повышение репутации'] is not None:
            if author_data['профиль']['последнее повышение репутации'] is not None and time.time() - author_data['профиль']['последнее повышение репутации'] < 300:
                embed = disnake.Embed(
                    title='Репутация',
                    description=f"Вы уже повышали/понижали репутацию этому пользователю сегодня",
                )
                embed.set_thumbnail(url=user.display_avatar.url)
                embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
                embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)
                await interaction.edit_original_message(embed=embed)
                return
        embed = disnake.Embed(
            title='Репутация',
            description=f"Выбирите понизить или повысить репутацию пользователю {user.mention}",
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url)
        message = await interaction.edit_original_message(embed=embed)
        view = RepView(self.bot, user, interaction.author, message)
        await message.edit(view=view)

def setup(bot):
    bot.add_cog(Rep(bot))