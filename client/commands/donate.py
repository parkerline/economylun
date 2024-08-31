import disnake; from disnake.ext import commands; from disnake import *; from disnake.ui import *;
import time;
from settings.config import *; from settings.db import *; from server.conf.emoji import *
from newcfg.shop import *

class DonateSelect(disnake.ui.Select):
    def __init__(self, roles, prices, user_roles):
        self.user_roles = user_roles  # Сохраняем user_roles в экземпляре класса
        options = [
            disnake.SelectOption(label=role.name, description=f"Цена: {prices[role.id]} звездочек", value=str(role.id), default=role.id in user_roles)
            for role in roles
        ]
        super().__init__(placeholder="Выберите роль для покупки", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: disnake.MessageInteraction):
        role_id = int(self.values[0])
        price = self.view.prices[role_id]

        # Используем self.user_roles напрямую вместо self.view.user_roles
        if role_id in self.user_roles:
            await interaction.response.send_message("У вас уже есть эта роль.", ephemeral=True)
            return

        user_data = await users.find_one({'айди': interaction.user.id})
        if user_data['профиль']['звездочки'] < price:
            embed = disnake.Embed(title='Магазин донатов', description='У вас недостаточно звездочек для покупки этой роли.').add_field(name='Цена', value=f'```{price}```').add_field(name='Ваши звездочки', value=f'```{user_data["профиль"]["звездочки"]}```').set_thumbnail(url=interaction.guild.icon.url).set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed, view=None)
            return

        await users.update_one({'айди': interaction.user.id}, {'$inc': {'профиль.звездочки': -price}})
        role = interaction.guild.get_role(role_id)
        await interaction.user.add_roles(role)
        await donate.update_one({'айди-роли': role_id}, {'$push': {'купили': interaction.user.id}})
        embed = disnake.Embed(title='Магазин донатов', description=f'Вы успешно купили роль {role.mention} за {price} звездочек.').set_thumbnail(url=interaction.guild.icon.url).set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        await interaction.response.edit_message(embed=embed, view=None)
                
class DonateView(disnake.ui.View):
    def __init__(self, author, roles, prices):
        super().__init__()
        self.author = author
        user_roles = [role.id for role in author.roles]
        self.prices = prices
        # Передаём user_roles напрямую в DonateSelect
        self.add_item(DonateSelect(roles, prices, user_roles))

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("Вы не можете использовать эти кнопки, так как не являетесь автором команды.", ephemeral=True)
            return False
        return True
    
class Donate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.slash_command(name='add_donate', description='Добавить роль в магазин донатов')
    async def add_donate(self, inter: disnake.ApplicationCommandInteraction, role: disnake.Role, звездочки: int):
        if inter.author.id not in ДОСТУП['добавление']:
            await inter.response.send_message("У вас нет доступа к этой команде.", ephemeral=True)
            return
        donate_result = await donate.find_one({'айди-роли': role.id})
        if donate_result:
            await inter.response.send_message("Эта роль уже добавлена в магазин донатов.", ephemeral=True)
            return
        donate_document = {
            'айди-сервера': inter.guild.id,
            'айди-роли': role.id,
            'добавил': inter.author.id,
            'цена': звездочки,
        }
        await donate.insert_one(donate_document)
        embed = disnake.Embed(title='Добавление роли в магазин донатов', description=f'Роль: {role.mention}\nЗвездочки: {звездочки}')
        await inter.response.send_message(embed=embed)
        
    @commands.slash_command(name='remove_donate', description='Удалить роль из магазина донатов')
    async def remove_donate(self, inter: disnake.ApplicationCommandInteraction, role: disnake.Role):
        if inter.author.id not in ДОСТУП['добавление']:
            await inter.response.send_message("У вас нет доступа к этой команде.", ephemeral=True)
            return
        donate = await donate.find_one({'айди-роли': role.id})
        if not donate:
            await inter.response.send_message("Эта роль не добавлена в магазин донатов.", ephemeral=True)
            return
        await donate.delete_one({'айди-роли': role.id})
        embed = disnake.Embed(title='Удаление роли из магазина донатов', description=f'Роль: {role.mention}')
        await inter.response.send_message(embed=embed)
        
    @commands.slash_command(name='donate', description='Открыть магазин донатов')
    async def donate(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        roles_data = await donate.find({'айди-сервера': inter.guild.id}).to_list(None)
        if not roles_data:
            embed = disnake.Embed(title='Магазин донатов', description='На данном сервере нет ролей в магазине донатов.')
            await inter.edit_original_message(embed=embed)
            return

        roles = [inter.guild.get_role(role_data['айди-роли']) for role_data in roles_data if inter.guild.get_role(role_data['айди-роли'])]
        prices = {role_data['айди-роли']: role_data['цена'] for role_data in roles_data}
        embed = disnake.Embed(title='Магазин донатов', description='Выберите роль для покупки').set_thumbnail(url=inter.guild.icon.url).set_author(name=inter.author.display_name, icon_url=inter.author.display_avatar.url)
        view = DonateView(inter.author, roles, prices)
        await inter.edit_original_message(embed=embed, view=view)
        
def setup(bot):
    bot.add_cog(Donate(bot))