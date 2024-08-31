import disnake; from disnake.ext import commands; from disnake import *; from disnake.ui import *;
import time; import random;
from settings.config import *; from settings.db import *; from server.conf.emoji import *


class InroleView(disnake.ui.View):
    def __init__(self, bot, message, author):
        super().__init__(timeout=60)
        self.bot = bot
        self.message = message
        self.author = author
        self.add_item(InroleRoleSelect(self.bot, self.message, self.author))


class InroleRoleSelect(disnake.ui.RoleSelect):
    def __init__(self, bot, message, author):
        super().__init__(placeholder='Выберите роль', min_values=1, max_values=1)
        self.bot = bot
        self.message = message
        self.author = author

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("Вы не можете использовать этот селект", ephemeral=True)
            return False
        return True

    async def callback(self, interaction: disnake.Interaction):
        role = self.values[0]
        embed = disnake.Embed(
            title=f'**Участники в роли** {role.name} \n **Общее количество:** *{len(role.members)}*',
            description='\n'.join([member.mention for member in role.members]),
        )
        await self.message.edit(embed=embed, view=None)
    
    
class Inrole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="inrole", description="Посмотреть участников в роли")
    async def inrole(self, interaction: disnake.ApplicationCommandInteraction):
        await interaction.response.defer()
        embed = disnake.Embed(
            title='Участники в роли',
            description='Выберите роль, чтобы посмотреть участников',
        )
        message = await interaction.edit_original_response(embed=embed)
        view = InroleView(self.bot, message, interaction.author)
        await message.edit(view=view)

def setup(bot):
    bot.add_cog(Inrole(bot))
