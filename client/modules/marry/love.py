import disnake; from disnake.ext import commands; from disnake import *; from disnake.ui import *;
import time; import re;
from settings.config import *; from settings.db import *; from server.conf.emoji import *; from server.conf.cfg import *


class LoveView(disnake.ui.View):
    def __init__(self, author, bot, message, membermessage, member):
        super().__init__(timeout=None)
        self.author = author
        self.bot = bot
        self.message = message
        self.membermessage = membermessage
        self.member = member

    @disnake.ui.button(label="Принять", style=disnake.ButtonStyle.green)
    async def accept(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        user = await users.find_one({'айди': self.author.id})
        member_dict = await users.find_one({'айди': self.member.id})
        brakis = {
            'пара': {
                'первый': user['айди'],
                'второй': member_dict['айди'],
            },
            'баланс пары': 0,
            'онлайн пары': 0,
            'дата': None,
            'статус': 'не установлен',
            'лав рума': False,
            'название любовной румы': 'не установлено',
            'айди румы': None,
            'дата': time.time(),
        }
        await braki.insert_one(brakis)
        await users.update_one({'айди': self.author.id}, {'$push': {'история браков': {'пара': {'первый': user['айди'], 'второй': member_dict['айди'], 'дата': time.time()}}}})
        await users.update_one({'айди': self.member.id}, {'$push': {'история браков': {'пара': {'первый': user['айди'], 'второй': member_dict['айди'], 'дата': time.time()}}}})
        embed = disnake.Embed(
            title="**Подтверждение брака**",
            description=f"Вы приняли предложение о браке участника {self.author.mention}",
        )
        embed.set_thumbnail(url=self.member.display_avatar.url)
        embed.set_author(name=self.author.display_name, icon_url=self.author.display_avatar.url)
        embed.set_footer(text=f"Любовь", icon_url=self.bot.user.display_avatar.url)
        await self.membermessage.edit(embed=embed, view=None)
        embed = disnake.Embed(
            title="**Подтверждение брака**",
            description=f"Участник {interaction.author.mention} принял ваше предложение о браке",
        )
        embed.set_thumbnail(url=self.author.display_avatar.url)
        embed.set_author(name=self.member.display_name, icon_url=self.member.display_avatar.url)
        embed.set_footer(text=f"Любовь", icon_url=self.bot.user.display_avatar.url)
        await self.message.edit(embed=embed, view=None)

    @disnake.ui.button(label="Отклонить", style=disnake.ButtonStyle.red)
    async def decline(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        embed = disnake.Embed(
            title="**Подтверждение брака**",
            description=f"Вы отклонили предложение о браке участника {self.author.mention}",
        )
        embed.set_thumbnail(url=self.member.display_avatar.url)
        embed.set_author(name=self.author.display_name, icon_url=self.author.display_avatar.url)
        embed.set_footer(text=f"Любовь", icon_url=self.bot.user.display_avatar.url)
        await self.membermessage.edit(embed=embed, view=None)
        embed = disnake.Embed(
            title="**Подтверждение брака**",
            description=f"Участник {interaction.author.mention} отклонил ваше предложение о браке",
        )
        embed.set_thumbnail(url=self.author.display_avatar.url)
        embed.set_author(name=self.member.display_name, icon_url=self.member.display_avatar.url)
        embed.set_footer(text=f"Любовь", icon_url=self.bot.user.display_avatar.url)
        await self.message.edit(embed=embed, view=None)

class Love(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="marry", description="Пожениться на участнике сервера")
    async def marry(self, interaction: disnake.ApplicationCommandInteraction, member: disnake.Member):
        await interaction.response.defer()
        user_roles = {role.id for role in interaction.user.roles}
        member_roles = {role.id for role in member.roles}
        if ЛЮБОВНЫЕРУМЫ['мальчик'] in user_roles and ЛЮБОВНЫЕРУМЫ['мальчик'] in member_roles:
            embed = disnake.Embed(
                title="**Предложение брака**",
                description=f"Однополые браки запрещены.",
            )
            embed.set_thumbnail(url=interaction.author.display_avatar.url)
            embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
            embed.set_footer(text=f"Любовь", icon_url=self.bot.user.display_avatar.url)
            await interaction.edit_original_message(embed=embed)
            return
        if ЛЮБОВНЫЕРУМЫ['девочка'] in user_roles and ЛЮБОВНЫЕРУМЫ['девочка'] in member_roles:
            embed = disnake.Embed(
                title="**Предложение брака**",
                description=f"Однополые браки запрещены.",
            )
            embed.set_thumbnail(url=interaction.author.display_avatar.url)
            embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
            embed.set_footer(text=f"Любовь", icon_url=self.bot.user.display_avatar.url)
            await interaction.edit_original_message(embed=embed)
            return
        user, member_dict = await asyncio.gather(
            users.find_one({'айди': interaction.user.id}),
            users.find_one({'айди': member.id})
        )
        if member_dict is None:
            embed = disnake.Embed(
                title="**Предложение брака**",
                description=f"Участник не найден",
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
            embed.set_footer(text=f"Любовь", icon_url=self.bot.user.display_avatar.url)
            await interaction.edit_original_message(embed=embed)
            return
        if user['айди'] == member_dict['айди']:
            embed = disnake.Embed(            
                title="**Предложение брака**",
                description=f"Вы не можете пожениться с самим собой",
            )
            embed.set_thumbnail(url=interaction.author.display_avatar.url)
            embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
            embed.set_footer(text=f"Любовь", icon_url=self.bot.user.display_avatar.url)
            await interaction.edit_original_message(embed=embed)
            return
        braki_list = await braki.find({'$or': [{'пара.первый': {'$in': [user['айди'], member_dict['айди']]}}, {'пара.второй': {'$in': [user['айди'], member_dict['айди']]}}]}).to_list(None)
        if any(brak['пара']['первый'] == user['айди'] or brak['пара']['второй'] == user['айди'] for brak in braki_list):
            embed = disnake.Embed(
                title="**Предложение брака**",
                description=f"Вы уже состоите в браке",
            )
            embed.set_thumbnail(url=interaction.author.display_avatar.url)
            embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
            embed.set_footer(text=f"Любовь", icon_url=self.bot.user.display_avatar.url)
            await interaction.edit_original_message(embed=embed)
            return
        if any(brak['пара']['первый'] == member_dict['айди'] or brak['пара']['второй'] == member_dict['айди'] for brak in braki_list):
            embed = disnake.Embed(
                title="**Предложение брака**",
                description=f"Участник уже состоит в браке",
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
            embed.set_footer(text=f"Любовь", icon_url=self.bot.user.display_avatar.url)
            await interaction.edit_original_message(embed=embed)
            return
        embed = disnake.Embed(
            title="**Подтверждение брака**",
            description=f"Вы отправили предложение о браке участнику {member.mention}",
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
        embed.set_footer(text=f"Любовь", icon_url=self.bot.user.display_avatar.url)
        message = await interaction.edit_original_message(embed=embed)
        memberembed = disnake.Embed(
            title="**Предложение брака**",
            description=f"{interaction.author.mention} предложил вам брак. Принять или отклонить?",
        )
        memberembed.set_thumbnail(url=interaction.author.display_avatar.url)
        memberembed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
        memberembed.set_footer(text=f"Любовь", icon_url=self.bot.user.display_avatar.url)
        membermessage = await member.send(embed=memberembed)
        view = LoveView(interaction.author, self.bot, message, membermessage, member)
        await membermessage.edit(view=view)

def setup(bot):
    bot.add_cog(Love(bot))
