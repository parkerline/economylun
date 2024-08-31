import disnake; from disnake.ext import commands; from disnake import *; from disnake.ui import *;
import time; import re; import asyncio;
from settings.config import *; from settings.db import *; from server.conf.emoji import *; from server.conf.cfg import *


class VipeView(disnake.ui.View):
    def __init__(self, author, embed, msg):
        super().__init__()
        self.author = author
        self.embed = embed
        self.msg = msg

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("Вы не можете использовать эти кнопки, так как не являетесь автором команды.", ephemeral=True)
            return False
        return True

    @disnake.ui.select(
        options=[
            disnake.SelectOption(label='Очистить базу данных', value='clear_db'),
            disnake.SelectOption(label='Вайп всем кроме стаффа', value='all_except_staff'),
            disnake.SelectOption(label='Вайп стаффа', value='staff')
        ],
        custom_id='vipe'
    )
    async def select_option(self, select, interaction):
        if interaction.data['values'][0] == 'clear_db':
            if self.embed.fields[0].value == 'True':
                self.embed.set_field_at(0, name='Очистить базу данных', value='False', inline=False)
                await interaction.response.send_message('База данных не будет очищена', ephemeral=True)
            else:
                self.embed.set_field_at(0, name='Очистить базу данных', value='True', inline=False)
                await interaction.response.send_message('База данных будет очищена', ephemeral=True)
        elif interaction.data['values'][0] == 'all_except_staff':
            if self.embed.fields[1].value == 'True':
                self.embed.set_field_at(1, name='Вайп всем кроме стаффа', value='False', inline=False)
                await interaction.response.send_message('Все кроме стаффа не будут вайпнуты', ephemeral=True)
            else:
                self.embed.set_field_at(1, name='Вайп всем кроме стаффа', value='True', inline=False)
                await interaction.response.send_message('Все кроме стаффа будут вайпнуты', ephemeral=True)
        elif interaction.data['values'][0] == 'staff':
            if self.embed.fields[2].value == 'True':
                self.embed.set_field_at(2, name='Вайп стаффа', value='False', inline=False)
                await interaction.response.send_message('Стафф не будет вайпнут', ephemeral=True)
            else:
                self.embed.set_field_at(2, name='Вайп стаффа', value='True', inline=False)
                await interaction.response.send_message('Стафф будет вайпнут', ephemeral=True)
        await self.msg.edit(embed=self.embed)

    @disnake.ui.button(label='Начать', style=disnake.ButtonStyle.secondary)
    async def start(self, button, interaction):
        await interaction.response.defer()
        embed = disnake.Embed(title='Вайп сервера', description='загрузка...').set_thumbnail(url=self.author.avatar.url).set_author(name=self.author, icon_url=self.author.avatar.url).set_footer(text='Вайп сервера', icon_url=interaction.guild.icon.url)
        await self.msg.edit(embed=embed, view=None)
        messages = []

        if self.embed.fields[0].value == 'True':  # Очистить базу данных
            await db.users.drop()
            await db.shops.drop()
            await db.braki.drop()
            await db.paneladmin.drop()
            await db.profiles.drop()
            await db.privates.drop()
            await db.стафф.drop()
            await db.наказание.drop()
            await db.верефнедопуск.drop()
            await db.репортек.drop()

        unverify_role = disnake.utils.get(interaction.guild.roles, id=DEVELOPER['unverify'])
        staff_role = disnake.utils.get(interaction.guild.roles, id=DEVELOPER['стафф'])

        if self.embed.fields[1].value == 'True':
            for member in interaction.guild.members:
                if member == self.author or staff_role in member.roles:  # пропустить автора и стафф
                    continue
                for role in member.roles:
                    if role == interaction.guild.default_role:  # пропустить роль @everyone
                        continue
                    try:
                        await member.remove_roles(role)
                    except disnake.Forbidden:
                        continue
                if unverify_role not in member.roles:
                    await member.add_roles(unverify_role)


        if self.embed.fields[2].value == 'True':  # Вайп стаффа
            for member in interaction.guild.members:
                if member == self.author or staff_role not in member.roles:  # пропустить автора и не-стафф
                    continue
                for role in member.roles:
                    if role == interaction.guild.default_role:  # пропустить роль @everyone
                        continue
                    try:
                        await member.remove_roles(role)
                    except disnake.Forbidden:
                        continue
                if unverify_role not in member.roles:
                    await member.add_roles(unverify_role)

        embed = disnake.Embed(title='Вайп сервера', description='\n'.join(messages)).set_thumbnail(url=self.author.avatar.url).set_author(name=self.author, icon_url=self.author.avatar.url).set_footer(text='Вайп сервера', icon_url=interaction.guild.icon.url)
        await interaction.response.send_message('Вы успешно вайпнули', ephemeral=True)
        await self.msg.edit(embed=embed, view=None)
        

class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.slash_command()
    async def dev(self, inter: disnake.ApplicationCommandInteraction):
        pass
        
    @dev.sub_command(name='voice', description='Выводит айди войсов в категории')
    async def dev_voice(self, inter: disnake.ApplicationCommandInteraction, category: str):
        role = disnake.utils.get(inter.guild.roles, id=DEVELOPER['role'])
        if role not in inter.author.roles:
            await inter.response.send_message('У вас нет доступа к этой команде', ephemeral=True)
            return
        category = int(category)
        category = self.bot.get_channel(category)
        if category is None:
            await inter.response.send_message('Категория не найдена', ephemeral=True)
            return
        if not isinstance(category, disnake.CategoryChannel):
            await inter.response.send_message('Это не категория', ephemeral=True)
            return
        voice_channels = category.voice_channels
        if not voice_channels:
            await inter.response.send_message('В категории нет войсов', ephemeral=True)
            return
        voice_channels_ids = ', '.join(str(vc.id) for vc in voice_channels)
        await inter.response.send_message(f'Войсы в категории {category.name}:\n{voice_channels_ids}', ephemeral=True)
        
    @dev.sub_command(name='vipe', description='Вайп сервера')
    async def dev_vipe(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        embed = disnake.Embed(title='Вайп сервера', description='загрузка...').set_thumbnail(url=self.bot.user.avatar.url).set_author(name=inter.author, icon_url=inter.author.avatar.url).set_footer(text='Вайп сервера', icon_url=inter.guild.icon.url)
        nachalo = await inter.edit_original_message(embed=embed)
        required_channel_id = DEVELOPER['канал вайпа']
        channel = disnake.utils.get(inter.guild.channels, id=DEVELOPER['канал вайпа'])
        if inter.channel_id != required_channel_id:
            await inter.followup.send(f'Вы вводите команду не в том канале, перейдите в {channel.mention}', ephemeral=True)
            await nachalo.delete()
            return
        role = disnake.utils.get(inter.guild.roles, id=DEVELOPER['role'])
        if role not in inter.author.roles:
            await inter.followup.send('У вас нет доступа к этой команде', ephemeral=True)
            await nachalo.delete()
            return
        embed = disnake.Embed(title='Вайп сервера', description='Выбирите настройки вайпа').set_thumbnail(url=self.bot.user.avatar.url).set_author(name=inter.author, icon_url=inter.author.avatar.url).set_footer(text='Вайп сервера', icon_url=inter.guild.icon.url)
        embed.add_field(name='Очистить базу данных', value='False', inline=False)
        unverify = disnake.utils.get(inter.guild.roles, id=DEVELOPER['unverify'])
        стафф = disnake.utils.get(inter.guild.roles, id=DEVELOPER['стафф'])
        embed.add_field(name=f'Вайп всем кроме {стафф.name}', value='False', inline=False)
        embed.add_field(name=f'Вайп {стафф.name}', value='False', inline=False)
        view = VipeView(inter.author, embed, nachalo)
        await nachalo.edit(embed=embed, view=view)
        
def setup(bot):
    bot.add_cog(Developer(bot))