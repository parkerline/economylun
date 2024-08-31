import disnake; from disnake.ext import commands; from disnake import *; from disnake.ui import *;
import time;
from settings.config import *; from settings.db import *; from server.conf.emoji import *

class UserSelectionView(disnake.ui.View):
    def __init__(self, user, member, bot, message):
        self.user = user
        self.member = member
        self.bot = bot
        self.message = message
        super().__init__()
        self.add_item(UserSelection(self.user, self.member, self.bot, self.message))

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if interaction.user != self.user:
            await interaction.response.send_message("Вы не можете использовать эти кнопки, так как не являетесь автором команды.", ephemeral=True)
            return False
        return True
    
class TakeModal(disnake.ui.Modal):
    def __init__(self, user, member, bot, message):
        self.user = user
        self.member = member
        self.bot = bot
        self.message = message
        self.amount = disnake.ui.TextInput(
            label="Сумма для перевода",
            custom_id="amount_input",
            placeholder="Введите сумму, которую хотите перевести",
            min_length=1,
            max_length=10,
            required=True,
        )
        super().__init__(title="Перевод средств", components=[self.amount])

    async def callback(self, interaction: disnake.MessageInteraction):
        await interaction.response.defer(ephemeral=True)
        try:
            amount = int(interaction.text_values["amount_input"])
        except ValueError:
            await interaction.followup.send("Введите число", ephemeral=True)
            return
        user = await users.find_one({'айди': self.user.id})
        member = await users.find_one({'айди': self.member.id})
        commission = amount * 0.1
        net_amount = round(amount - commission)
        if user['профиль']['баланс'] < amount:
            await interaction.followup.send("У вас недостаточно средств для перевода", ephemeral=True)
            return
        if member is None:
            await interaction.followup.send("Пользователь не найден", ephemeral=True)
            return
        await users.update_one({'айди': self.user.id}, {'$inc': {'профиль.баланс': -amount}})
        await users.update_one({'айди': self.member.id}, {'$inc': {'профиль.баланс': net_amount}})
        await users.update_one({'айди': self.user.id}, {'$push': {'транзакции': {'отправитель': self.user.id, 'получатель': self.member.id, 'сумма': net_amount, 'дата': time.time()}}})
        await users.update_one({'айдi': self.member.id}, {'$push': {'транзакции': {'отправитель': self.user.id, 'получатель': self.member.id, 'сумма': net_amount, 'дата': time.time()}}})
        embed = disnake.Embed(
            title="Перевод средств успешно выполнен",
            description=f"Вы успешно перевели {self.member.mention}",
        )
        embed.add_field(name=f"{ЭМОДЗИ['razdelitel']}**Монет** {ЭМОДЗИ['money']}", value=f"```{net_amount}```")
        embed.add_field(name=f"{ЭМОДЗИ['razdelitel']}**Ваш баланс монет** {ЭМОДЗИ['money']}", value=f"```{round(user['профиль']['баланс'] - amount)}```")
        embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
        embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
        await interaction.edit_original_message("Вы успешно перевели монеты")
        await self.message.edit(embed=embed, view=None)

class UserSelection(disnake.ui.UserSelect):
    def __init__(self, user, member, bot, message):
        self.user = user
        self.member = member
        self.bot = bot
        self.message = message
        super().__init__(placeholder="Выберите пользователя", min_values=1, max_values=1)

    async def callback(self, interaction: disnake.MessageInteraction):
        member_id = interaction.data['values'][0]
        member = interaction.guild.get_member(int(member_id))
        modal = TakeModal(self.user, member, self.bot, self.message)
        await interaction.response.send_modal(modal)

class BalanceView(disnake.ui.View):
    def __init__(self, user, member, bot, message):
        self.user = user
        self.member = member
        self.bot = bot
        self.message = message
        super().__init__()

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if interaction.user != self.user:
            await interaction.response.send_message("Вы не можете использовать эти кнопки, так как не являетесь автором команды.", ephemeral=True)
            return False
        return True
    
    @disnake.ui.button(label="Перевести монеты", style=ButtonStyle.gray, custom_id="send_money")
    async def send_money(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        view = UserSelectionView(self.user, self.member, self.bot, self.message)
        await interaction.response.send_message("Выберите пользователя, которому хотите перевести монеты", view=view, ephemeral=True)

class Balance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.slash_command(name="balance", description="Показывает баланс пользователя")
    async def balance(self, interaction: disnake.ApplicationCommandInteraction, member: disnake.Member = None):
        await interaction.response.defer()
        if member is None:
            member = interaction.author
        user = await users.find_one({'айди': member.id})
        balance = user['профиль']['баланс']
        zv = user['профиль']['звездочки']
        embed = disnake.Embed(
            title=f"**Баланс пользователя — {member.display_name}**",
        )
        embed.add_field(name=f"{ЭМОДЗИ['razdelitel']} **Монеты** {ЭМОДЗИ['money']}", value=f"```{balance}```")
        embed.add_field(name=f"{ЭМОДЗИ['razdelitel']} **Звездочки**  {ЭМОДЗИ['zvezda']}", value=f"```{zv}```")
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
        embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
        message = await interaction.edit_original_message(embed=embed)
        if interaction.user == member:
            view = BalanceView(interaction.user, member, self.bot, message)
            await message.edit(view=view)

def setup(bot):
    bot.add_cog(Balance(bot))