import disnake; from disnake.ext import commands; from disnake import *; from disnake.ui import *;
import time; import re; import asyncio;
from settings.config import *; from settings.db import *; from server.conf.emoji import *; from server.conf.cfg import *


class AdminView(disnake.ui.View):
    def __init__(self, user, apanels):
        self.user = user
        self.apanels = apanels
        super().__init__()

        new_buttons = NewButtons(user)

        if self.apanels.get('выдача монет', 0):
            self.add_item(new_buttons.give_money)
            self.add_item(new_buttons.ungive_money)
        if self.apanels.get('выдача звездочек', 0):
            self.add_item(new_buttons.give_donate)
            self.add_item(new_buttons.ungive_donate)

class GiveMoney(disnake.ui.Modal):
    def __init__(self, user):
        self.user = user
        self.id = disnake.ui.TextInput(
            label="Введите ID пользователя",
            custom_id="id_input",
            placeholder="Введите ID пользователя, которому хотите выдать монеты",
            min_length=1,
            max_length=50,
            required=True,
        )
        self.amount = disnake.ui.TextInput(
            label="Сумма для выдачи",
            custom_id="amount_input",
            placeholder="Введите сумму, которую хотите выдать",
            min_length=1,
            max_length=10,
            required=True,
        )
        super().__init__(title="Выдача монет", components=[self.id, self.amount])

    async def callback(self, interaction: disnake.MessageInteraction):
        try:
            id = int(interaction.text_values["id_input"])
            amount = int(interaction.text_values["amount_input"])
        except ValueError:
            await interaction.response.send_message("Введите число", ephemeral=True)
            return
        member = interaction.guild.get_member(id)
        if member is None:
            await interaction.response.send_message("Пользователь с таким ID не найден на сервере.", ephemeral=True)
            return
        user = await users.find_one({'айди': member.id})
        if user is None:
            await interaction.response.send_message("Пользователь не найден в базе данных", ephemeral=True)
            return
        await users.update_one({'айди': member.id}, {'$inc': {'профиль.баланс': amount}})
        await interaction.response.send_message(f"Вы успешно выдали {amount} монет пользователю {member.mention}.", ephemeral=True)
        logembed = disnake.Embed(
            title="Выдача монет",
            description=f"Пользователь {member.mention}",
        )
        logembed.add_field(name="Сумма", value=f"```{amount}```")
        logembed.set_thumbnail(url=member.display_avatar.url)
        logembed.set_author(name=f"Выдал монеты администратор {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        logembed.set_footer(text=f"Монеты", icon_url=interaction.bot.user.display_avatar.url)
        logchannel = interaction.guild.get_channel(ЛОГКАНАЛЫ['monetki'])
        await logchannel.send(embed=logembed)

class UnGiveMoney(disnake.ui.Modal):
    def __init__(self, user):
        self.user = user
        self.id = disnake.ui.TextInput(
            label="Введите ID пользователя",
            custom_id="id_input",
            placeholder="Введите ID пользователя, у которого хотите забрать монеты",
            min_length=1,
            max_length=50,
            required=True,
        )
        self.amount = disnake.ui.TextInput(
            label="Сумма для снятие",
            custom_id="amount_input",
            placeholder="Введите сумму, которую хотите забрать",
            min_length=1,
            max_length=10,
            required=True,
        )
        super().__init__(title="Забрать монеты", components=[self.id, self.amount])

    async def callback(self, interaction: disnake.MessageInteraction):
        try:
            id = int(interaction.text_values["id_input"])
            amount = int(interaction.text_values["amount_input"])
        except ValueError:
            await interaction.response.send_message("Введите число", ephemeral=True)
            return
        member = interaction.guild.get_member(id)
        if member is None:
            await interaction.response.send_message("Пользователь с таким ID не найден на сервере.", ephemeral=True)
            return
        user = await users.find_one({'айди': member.id})
        if user is None:
            await interaction.response.send_message("Пользователь не найден в базе данных", ephemeral=True)
            return
        await users.update_one({'айди': member.id}, {'$inc': {'профиль.баланс': -amount}})
        await interaction.response.send_message(f"Вы успешно забрали {amount} монет у пользователя {member.mention}.", ephemeral=True)
        logembed = disnake.Embed(
            title="Забрать монеты",
            description=f"Пользователь {member.mention}",
        )
        logembed.add_field(name="Сумма", value=f"```{amount}```")
        logembed.set_thumbnail(url=member.display_avatar.url)
        logembed.set_author(name=f"Забрал монеты администратор {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        logembed.set_footer(text=f"Монеты", icon_url=interaction.bot.user.display_avatar.url)
        logchannel = interaction.guild.get_channel(ЛОГКАНАЛЫ['monetki'])
        await logchannel.send(embed=logembed)

class UnGiveZvezda(disnake.ui.Modal):
    def __init__(self, user):
        self.user = user
        self.id = disnake.ui.TextInput(
            label="Введите ID пользователя",
            custom_id="id_input",
            placeholder="Введите ID пользователя, у которого хотите забрать монеты",
            min_length=1,
            max_length=50,
            required=True,
        )
        self.amount = disnake.ui.TextInput(
            label="Сумма для снятия",
            custom_id="amount_input",
            placeholder="Введите сумму, которую хотите забрать",
            min_length=1,
            max_length=10,
            required=True,
        )
        super().__init__(title="Забрать звездочек", components=[self.id, self.amount])

    async def callback(self, interaction: disnake.MessageInteraction):
        try:
            id = int(interaction.text_values["id_input"])
            amount = int(interaction.text_values["amount_input"])
        except ValueError:
            await interaction.response.send_message("Введите число", ephemeral=True)
            return
        member = interaction.guild.get_member(id)
        if member is None:
            await interaction.response.send_message("Пользователь с таким ID не найден на сервере.", ephemeral=True)
            return
        user = await users.find_one({'айди': member.id})
        if user is None:
            await interaction.response.send_message("Пользователь не найден в базе данных", ephemeral=True)
            return
        await users.update_one({'айди': member.id}, {'$inc': {'профиль.звездочки': -amount}})
        await interaction.response.send_message(f"Вы успешно забрали {amount} звёздочки у пользователя {member.mention}.", ephemeral=True)
        logembed = disnake.Embed(
            title="Забрать монеты",
            description=f"Пользователь {member.mention}",
        )
        logembed.add_field(name="Сумма", value=f"```{amount}```")
        logembed.set_thumbnail(url=member.display_avatar.url)
        logembed.set_author(name=f"Забрал звездочки администратор {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        logembed.set_footer(text=f"Звёздочки", icon_url=interaction.bot.user.display_avatar.url)
        logchannel = interaction.guild.get_channel(ЛОГКАНАЛЫ['monetki'])
        await logchannel.send(embed=logembed)

class GiveZvezda(disnake.ui.Modal):
    def __init__(self, user):
        self.user = user
        self.id = disnake.ui.TextInput(
            label="Введите ID пользователя",
            custom_id="id_input",
            placeholder="Введите ID пользователя, которому хотите выдать монеты",
            min_length=1,
            max_length=50,
            required=True,
        )
        self.amount = disnake.ui.TextInput(
            label="Сумма для выдачи",
            custom_id="amount_input",
            placeholder="Введите сумму, которую хотите выдать",
            min_length=1,
            max_length=10,
            required=True,
        )
        super().__init__(title="Выдача звездочек", components=[self.id, self.amount])

    async def callback(self, interaction: disnake.MessageInteraction):
        try:
            id = int(interaction.text_values["id_input"])
            amount = int(interaction.text_values["amount_input"])
        except ValueError:
            await interaction.response.send_message("Введите число", ephemeral=True)
            return
        member = interaction.guild.get_member(id)
        if member is None:
            await interaction.response.send_message("Пользователь с таким ID не найден на сервере.", ephemeral=True)
            return
        user = await users.find_one({'айди': member.id})
        if user is None:
            await interaction.response.send_message("Пользователь не найден в базе данных", ephemeral=True)
            return
        await users.update_one({'айди': member.id}, {'$inc': {'профиль.звездочки': amount}})
        await interaction.response.send_message(f"Вы успешно выдали {amount} звездочек пользователю {member.mention}.", ephemeral=True)
        logembed = disnake.Embed(
            title="Выдача звёздочек",
            description=f"Пользователь {member.mention}",
        )
        logembed.add_field(name="Сумма", value=f"```{amount}```")
        logembed.set_thumbnail(url=member.display_avatar.url)
        logembed.set_author(name=f"Выдал звёздочек администратор {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        logembed.set_footer(text=f"Монеты", icon_url=interaction.bot.user.display_avatar.url)
        logchannel = interaction.guild.get_channel(ЛОГКАНАЛЫ['звёздочки'])
        await logchannel.send(embed=logembed)

class NewButtons(disnake.ui.View):
    def __init__(self, user):
        self.user = user
        super().__init__()

    @disnake.ui.button(label="Выдать монет", style=ButtonStyle.gray, custom_id="give_money")
    async def give_money(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        modal = GiveMoney(interaction.user)
        await interaction.response.send_modal(modal)

    @disnake.ui.button(label="Выдать звездочек", style=ButtonStyle.gray, custom_id="give_donate")
    async def give_donate(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        modal = GiveZvezda(interaction.user)
        await interaction.response.send_modal(modal)

    @disnake.ui.button(label="Забрать монеты", style=ButtonStyle.gray, custom_id="ungive_money")
    async def ungive_money(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        modal = UnGiveMoney(interaction.user)
        await interaction.response.send_modal(modal)

    @disnake.ui.button(label="Забрать звездочки", style=ButtonStyle.gray, custom_id="ungive_donate")
    async def ungive_donate(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        modal = UnGiveZvezda(interaction.user)
        await interaction.response.send_modal(modal)


class Apanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="apanel", description="Админ-панель")
    async def apanel(self, interaction: disnake.ApplicationCommandInteraction):
        apanels = await paneladmin.find_one({'айди': interaction.author.id})
        if apanels is None:
            await interaction.response.send_message("У вас нет доступа к админ-панели.", ephemeral=True)
            return
        view = AdminView(interaction.author, apanels)
        embed = disnake.Embed(
            title="Админ-панель",
            description="Выберите действие",
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

def setup(bot):
    bot.add_cog(Apanel(bot))
        