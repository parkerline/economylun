import disnake; from disnake.ext import commands; from disnake import *; from disnake.ui import *;
import time; import re; import asyncio;
from settings.config import *; from settings.db import *; from server.conf.emoji import *; from server.conf.cfg import *

class DostupModal(disnake.ui.Modal):
    def __init__(self, inter):
        self.inter = inter
        self.id = disnake.ui.TextInput(
            label="Введите ID пользователя",
            custom_id="id_input",
            placeholder="Введите ID пользователя, которому хотите выдать доступ",
            min_length=1,
            max_length=50,
            required=True,
        )
        self.set1 = disnake.ui.TextInput(
            label="Выдача монет",
            custom_id="set1_input",
            placeholder="1 - выдать доступ, 0 - забрать доступ",
            min_length=1,
            max_length=10,
            required=True,
        )
        self.set2 = disnake.ui.TextInput(
            label="Выдача звездочек",
            custom_id="set2_input",
            placeholder="1 - выдать доступ, 0 - забрать доступ",
            min_length=1,
            max_length=10,
            required=True,
        )
        super().__init__(title="Выдача доступа", components=[self.id, self.set1, self.set2])

    async def callback(self, interaction: disnake.MessageInteraction):
        try:
            id = int(interaction.text_values["id_input"])
            set1 = int(interaction.text_values["set1_input"])
            set2 = int(interaction.text_values["set2_input"])
        except ValueError:
            await interaction.response.send_message("Введите число", ephemeral=True)
            return

        member = interaction.guild.get_member(id)
        if member is None:
            await interaction.response.send_message("Пользователь с таким ID не найден на сервере.", ephemeral=True)
            return

        apanel = {
            'айди': id,
            'выдача монет': set1,
            'выдача звездочек': set2,
        } 
        await paneladmin.insert_one(apanel)
        await interaction.response.send_message(f"Вы успешно выдали доступ пользователю {member.mention}.")
    

class Dostup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="add_dostup", description="Добавить доступ к админ-панели")
    async def add_dostup(self, inter):
        if inter.user.id in ДОСТУП['доступ']:
            modal = DostupModal(inter)
            await inter.response.send_modal(modal)
        else:
            await inter.response.send_message("У вас нет доступа к этой команде.")

    @commands.slash_command(name="remove_dostup", description="Удалить доступ к админ-панели")
    async def remove_dostup(self, inter, member: disnake.Member):
        if inter.user.id in ДОСТУП['доступ']:
            await paneladmin.delete_one({'айди': member.id})
            await inter.response.send_message(f"Вы успешно забрали доступ у пользователя {member.mention}.")
        else:
            await inter.response.send_message("У вас нет доступа к этой команде.")


def setup(bot):
    bot.add_cog(Dostup(bot))