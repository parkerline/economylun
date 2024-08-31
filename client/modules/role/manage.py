import disnake; from disnake.ext import commands; from disnake import *; from disnake.ui import *;
import time; import re;
from settings.config import *; from settings.db import *; from server.conf.emoji import *; from server.conf.cfg import *


class NewRoleModal(disnake.ui.Modal):
    def __init__(self, user, bot, message, role):
        self.user = user
        self.bot = bot
        self.message = message
        self.role = role
        self.role_name = disnake.ui.TextInput(
            label="Название роли",
            custom_id="role_name_input",
            placeholder="Введите название роли",
            min_length=1,
            max_length=500,
            required=True,
            value=role['название'],
        )
        self.color = disnake.ui.TextInput(
            label="Цвет роли",
            custom_id="role_color_input",
            placeholder="Введите HEX-код цвета роли",
            min_length=1,
            max_length=10,
            required=True,
            value=role['цвет'],
        )
        self.price_role = disnake.ui.TextInput(
            label="Цена роли",
            custom_id="role_price_input",
            placeholder="Введите цену роли",
            min_length=1,
            max_length=10,
            required=True,
            value=role['цена'],
        )
        super().__init__(title="Управление ролью", components=[self.role_name, self.color, self.price_role])

    async def callback(self, interaction: disnake.MessageInteraction):
        await interaction.response.defer(ephemeral=True)
        role_name = interaction.text_values["role_name_input"]
        role_color = interaction.text_values["role_color_input"]
        try:
            role_price = int(interaction.text_values["role_price_input"])
        except ValueError:
            await interaction.followup.send("Введите число")
            return
        
        if not re.match("^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$", role_color):
            await interaction.followup.send("Введите действительный HEX-код")
            return
        
        await shops.update_one({'айди роли': self.role['айди роли']}, {'$set': {'название': role_name, 'цвет': role_color, 'цена': role_price}})
        role = interaction.guild.get_role(self.role['айди роли'])
        await role.edit(name=role_name, color=disnake.Color(int(role_color[1:], 16)))
        embed = disnake.Embed(
            title=f"Управление ролью {role_name}",
            description=f"**Цена:** {role_price}\n**Цвет:** {role_color}",
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
        await interaction.edit_original_message("Роль успешно изменена")
        await self.message.edit(embed=embed, view=None)

class DeleteRole(disnake.ui.View):
    def __init__(self, user, bot, message, role):
        self.user = user
        self.bot = bot
        self.message = message
        self.role = role
        super().__init__()

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if interaction.user != self.user:
            await interaction.response.send_message("Вы не можете использовать эти кнопки, так как не являетесь автором команды.", ephemeral=True)
            return False
        return True

    @disnake.ui.button(label="Подтвердить", style=disnake.ButtonStyle.gray)
    async def confirm(self, button: disnake.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        role = interaction.guild.get_role(self.role['айди роли'])
        await shops.delete_one({'айди роли': self.role['айди роли']})
        await role.delete()
        embed = disnake.Embed(
            title=f"Удаление роли {role.name}",
            description=f"Роль {role.name} успешно удалена",
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
        await self.message.edit(embed=embed, view=None)
    
    @disnake.ui.button(label="Отмена", style=disnake.ButtonStyle.gray)
    async def cancel(self, button: disnake.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        role = interaction.guild.get_role(self.role['айди роли'])
        embed = disnake.Embed(
            title=f"Удаление роли {role.name}",
            description=f"Вы отменили удаление роли {role.mention}",
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
        await self.message.edit(embed=embed, view=None)

class NewRoleView(disnake.ui.View):
    def __init__(self, user, bot, message, role):
        self.user = user
        self.bot = bot
        self.message = message
        self.role = role
        super().__init__()
    
    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if interaction.user != self.user:
            await interaction.response.send_message("Вы не можете использовать эти кнопки, так как не являетесь автором команды.", ephemeral=True)
            return False
        return True
    
    @disnake.ui.button(label="Изменить роль", style=disnake.ButtonStyle.gray)
    async def change_role(self, button: disnake.Button, interaction: disnake.MessageInteraction):
        modal = NewRoleModal(self.user, self.bot, self.message, self.role)
        await interaction.response.send_modal(modal)

    @disnake.ui.button(label="Удалить роль", style=disnake.ButtonStyle.gray)
    async def delete_role(self, button: disnake.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        role = interaction.guild.get_role(self.role['айди роли'])
        embed = disnake.Embed(
            title=f"Удаление роли {role.name}",
            description=f"Подтвердите удаление роли {role.mention}",
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
        view = DeleteRole(self.user, self.bot, self.message, self.role)
        await self.message.edit(embed=embed, view=view)


class RoleSelectView(disnake.ui.View):
    def __init__(self, bot, user, message, roles):
        self.bot = bot
        self.user = user
        self.message = message
        self.roles = roles
        super().__init__()
        self.add_item(RoleSelect(self.bot, self.user, self.message, self.roles))

class RoleSelect(disnake.ui.Select):
    def __init__(self, bot, user, message, roles):
        self.bot = bot
        self.user = user
        self.message = message
        self.roles = roles
        options = []
        for role in roles:
            options.append(disnake.SelectOption(label=role['название'], value=role['айди роли']))
        super().__init__(placeholder="Выберите роль", options=options, max_values=1)

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if interaction.user != self.user:
            await interaction.response.send_message("Вы не можете использовать эти кнопки, так как не являетесь автором команды.", ephemeral=True)
            return False
        return True

    async def callback(self, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        role = await shops.find_one({'айди роли': int(interaction.data['values'][0])})
        embed = disnake.Embed(
            title=f"Управление ролью {role['название']}",
            description=f"**Цена:** {role['цена']}\n**Цвет:** {role['цвет']}",
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
        view1 = NewRoleView(self.user, self.bot, self.message, role)
        await self.message.edit(embed=embed, view=view1)

class ManageRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="role-manage", description="Управление личными ролями")
    async def role_manage(self, interaction: disnake.ApplicationCommandInteraction):
        await interaction.response.defer()
        shop = await shops.find_one({'владелец': interaction.user.id})
        roles = [role async for role in shops.find({'владелец': interaction.user.id})]
        if shop is None:
            embed = disnake.Embed(
                title="Управление личными ролями",
                description="У вас нет личных ролей",
            )
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
            embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
            await interaction.edit_original_message(embed=embed)
            return
        
        embed = disnake.Embed(
            title=f"Управление личными ролями",
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
        message = await interaction.edit_original_message(embed=embed)
        view = RoleSelectView(self.bot, interaction.user, message, roles)
        await message.edit(view=view)

def setup(bot):
    bot.add_cog(ManageRole(bot))

