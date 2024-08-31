import disnake; from disnake.ext import commands; from disnake import *; from disnake.ui import *;
import time; import re;
from settings.config import *; from settings.db import *; from server.conf.emoji import *; from server.conf.cfg import *

class RoleModal(disnake.ui.Modal):
    def __init__(self, user, bot, message):
        self.user = user
        self.bot = bot
        self.message = message
        self.role_name = disnake.ui.TextInput(
            label="Название роли",
            custom_id="role_name_input",
            placeholder="Введите название роли",
            min_length=1,
            max_length=500,
            required=True,
        )
        self.color = disnake.ui.TextInput(
            label="Цвет роли",
            custom_id="role_color_input",
            placeholder="Введите HEX-код цвета роли",
            min_length=1,
            max_length=10,
            required=True,
        )
        self.price_role = disnake.ui.TextInput(
            label="Цена роли",
            custom_id="role_price_input",
            placeholder="Введите цену роли",
            min_length=1,
            max_length=4,
            required=True,
        )
        super().__init__(title="Создание личной роли", components=[self.role_name, self.color, self.price_role])

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

        user = await users.find_one({'айди': self.user.id}) 
        if user['профиль']['баланс'] < 15000:
            await interaction.followup.send("У вас недостаточно средств для создания роли")
            return
        
        await users.update_one({'айди': self.user.id}, {'$inc': {'профиль.баланс': -15000}})

        role = await interaction.guild.create_role(name=role_name, color=disnake.Color(int(role_color[1:], 16)))

        position = interaction.guild.get_role(РОЛЬ['местосоздание']).position - 1
        await role.edit(position=position)

        await interaction.user.add_roles(role)

        await shops.insert_one({
            'владелец': self.user.id,
            'айди роли': role.id,
            'название': role_name,
            'цена': role_price,
            'цвет': role_color,
            'кол-во покупок': 0,
        })
        await interaction.followup.send("Роль успешно создана")

        embed = disnake.Embed(
            title=f"Роль успешно создана — {self.user.display_name}",
            description=f"Вы успешно создали роль {role.mention}",
        )
        embed.add_field(name=f"{ЭМОДЗИ['razdelitel']}**Цена** {ЭМОДЗИ['money']}", value=f"```{role_price}```")
        embed.add_field(name=f"{ЭМОДЗИ['razdelitel']}**Ваш баланс монет** {ЭМОДЗИ['money']}", value=f"```{user['профиль']['баланс'] - 10000}```")
        embed.set_thumbnail(url=self.user.display_avatar.url)
        embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
        embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
        await self.message.edit(embed=embed, view=None)


class RoleView(disnake.ui.View):
    def __init__(self, user, bot, message):
        self.user = user
        self.bot = bot
        self.message = message
        super().__init__()

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if interaction.user != self.user:
            await interaction.response.send_message("Вы не можете использовать эти кнопки, так как не являетесь автором команды.", ephemeral=True)
            return False
        return True
    
    @disnake.ui.button(label="Да", style=disnake.ButtonStyle.gray, custom_id="role_yes")
    async def role_yes(self, button: disnake.Button, interaction: disnake.MessageInteraction):
        user = await users.find_one({'айди': interaction.user.id}) 
        if user['профиль']['баланс'] < 15000:
            await interaction.response.send_message("У вас недостаточно средств для создания роли", ephemeral=True)
            return
        modal = RoleModal(self.user, self.bot, self.message)
        await interaction.response.send_modal(modal=modal)

    @disnake.ui.button(label="Нет", style=disnake.ButtonStyle.gray, custom_id="role_no")
    async def role_no(self, button: disnake.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        embed = disnake.Embed(
            title="**Создание личной роли**",
            description=f"Вы отменили создание личной роли за 10000{ЭМОДЗИ['money']}",
        )
        embed.set_thumbnail(url=self.user.display_avatar.url)
        embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
        embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
        await interaction.edit_original_response(embed=embed, view=None)
        

class Role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="role", description="Создать свою личную роль")
    async def role(self, interaction: disnake.ApplicationCommandInteraction):
        await interaction.response.defer()
        user = await users.find_one({'айди': interaction.author.id})
        embed = disnake.Embed(
            title="**Создание личной роли**",
            description=f"Вы уверены что хотите создать свою личную роль за 15000{ЭМОДЗИ['money']}?",
        )
        embed.set_thumbnail(url=interaction.author.display_avatar.url)
        embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
        embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
        message = await interaction.edit_original_message(embed=embed)
        view = RoleView(interaction.author, self.bot, message)
        await message.edit(view=view)


def setup(bot):
    bot.add_cog(Role(bot))