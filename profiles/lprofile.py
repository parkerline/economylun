import disnake; from disnake.ext import commands; from disnake import *; from disnake.ui import *;
import time; import re; import asyncio;
from settings.config import *; from settings.db import *; from server.conf.emoji import *; from server.conf.cfg import *

def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours}ч {minutes}мин"

class AddBalancePara(disnake.ui.Modal):
    def __init__(self, user, member, message):
        self.user = user
        self.member = member
        self.message = message
        self.balance = disnake.ui.TextInput(
            label="Сумма для пополнение",
            custom_id="balance_input",
            placeholder="Введите сумму, которую хотите перевести",
            min_length=1,
            max_length=10,
            required=True,
        )
        super().__init__(title="Пополнить баланс брака", components=[self.balance])

    async def callback(self, interaction: disnake.MessageInteraction):
        await interaction.response.defer(ephemeral=True)
        try:
            balance = int(interaction.text_values["balance_input"])
        except ValueError:
            await interaction.followup.send("Введите число", ephemeral=True)
            return
        brake = await braki.find_one({'пара.первый': self.user.id}) or await braki.find_one({'пара.второй': self.user.id})
        userss = await users.find_one({'айди': self.user.id})
        if not brake:
            await interaction.followup.send("Вы не состоите в браке", ephemeral=True)
            return
        if brake['пара']['первый'] != self.user.id and brake['пара']['второй'] != self.user.id:
            await interaction.followup.send("Вы не состоите в браке", ephemeral=True)
            return
        if userss['профиль']['баланс'] < balance:
            await interaction.followup.send("У вас недостаточно средств для перевода", ephemeral=True)
            return
        await users.update_one({'айди': self.user.id}, {'$inc': {'профиль.баланс': -balance}})
        await braki.update_one({'_id': brake['_id']}, {'$inc': {'баланс пары': balance}})
        embed = disnake.Embed(
            title="Пополнение баланса брака",
            description=f"Вы успешно пополнили баланс брака на {balance}",
        )
        embed.set_thumbnail(url=self.user.display_avatar.url)
        embed.set_author(name=self.user.display_name, icon_url=self.user.display_avatar.url)
        embed.set_footer(text="Баланс")
        await interaction.followup.send(embed=embed)


class RenameLoveRoom(disnake.ui.Modal):
    def __init__(self, user, member, message):
        self.user = user
        self.member = member
        self.message = message
        self.name = disnake.ui.TextInput(
            label="Название румы",
            custom_id="name_input",
            placeholder="Введите название румы",
            min_length=1,
            max_length=20,
            required=True,
        )
        super().__init__(title="Установить название любовной румы", components=[self.name])

    async def callback(self, interaction: disnake.MessageInteraction):
        await interaction.response.defer(ephemeral=True)
        name = interaction.text_values["name_input"]
        brake = await braki.find_one({'пара.первый': self.user.id}) or await braki.find_one({'пара.второй': self.user.id})
        if not brake:
            await interaction.followup.send("Вы не состоите в браке", ephemeral=True)
            return
        if brake['пара']['первый'] != self.user.id and brake['пара']['второй'] != self.user.id:
            await interaction.followup.send("Вы не состоите в браке", ephemeral=True)
            return
        if not brake['лав рума']:
            await interaction.followup.send("У вас нет любовной румы", ephemeral=True)
            return
        await braki.update_one({'_id': brake['_id']}, {'$set': {'название любовной румы': name}})
        embed = disnake.Embed(
            title="Установка названия румы",
            description=f"Вы успешно установили название румы",
        )
        embed.set_thumbnail(url=self.user.display_avatar.url)
        embed.set_author(name=self.user.display_name, icon_url=self.user.display_avatar.url)
        embed.set_footer(text="Баланс")
        await interaction.followup.send(embed=embed)

class LprofileView(disnake.ui.View):
    def __init__(self, user, member, message):
        super().__init__(timeout=None)
        self.user = user
        self.member = member
        self.message = message

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if interaction.user != self.user:
            await interaction.response.send_message("Вы не можете использовать эти кнопки, так как не являетесь автором команды.", ephemeral=True)
            return False
        return True

    @disnake.ui.button(label="Пополнить баланс пары", style=disnake.ButtonStyle.gray, custom_id="add_balance")
    async def add_balance(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        modal = AddBalancePara(self.user, self.member, self.message)
        await interaction.response.send_modal(modal)

    @disnake.ui.button(label="Купить любовную руму", style=disnake.ButtonStyle.gray, custom_id="buy_love_room")
    async def buy_love_room(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        userss = await users.find_one({'айди': self.user.id})
        brake = await braki.find_one({'пара.первый': self.user.id}) or await braki.find_one({'пара.второй': self.user.id})
        if not brake:
            await interaction.response.send_message("Вы не состоите в браке", ephemeral=True)
            return
        if brake['пара']['первый'] != self.user.id and brake['пара']['второй'] != self.user.id:
            await interaction.response.send_message("Вы не состоите в браке", ephemeral=True)
            return
        if brake['лав рума']:
            await interaction.response.send_message("У вас уже есть любовная рума", ephemeral=True)
            return
        if brake['баланс пары'] < 5000:
            await interaction.response.send_message("У вас недостаточно средств для покупки", ephemeral=True)
            return
        await braki.update_one({'_id': brake['_id']}, {'$set': {'лав рума': True, 'рума до': time.time() + 7*24*60*60, 'баланс пары': brake['баланс пары'] - 5000}})
        await interaction.response.send_message("Вы успешно купили любовную руму на 7 дней", ephemeral=True)
    
    @disnake.ui.button(label="Установить название любовной румы", style=disnake.ButtonStyle.gray, custom_id="set_love_room_name")
    async def set_love_room_name(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        userss = await users.find_one({'айди': self.user.id})
        brake = await braki.find_one({'пара.первый': self.user.id}) or await braki.find_one({'пара.второй': self.user.id})
        if not brake:
            await interaction.response.send_message("Вы не состоите в браке", ephemeral=True)
            return
        if brake['пара']['первый'] != self.user.id and brake['пара']['второй'] != self.user.id:
            await interaction.response.send_message("Вы не состоите в браке", ephemeral=True)
            return
        if not brake['лав рума']:
            await interaction.response.send_message("У вас нет любовной румы", ephemeral=True)
            return
        modal = RenameLoveRoom(self.user, self.member, self.message)
        await interaction.response.send_modal(modal)
        
class Lprofile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.loveroom_check())

    async def loveroom_check(self):
        while True:
            бракк = await braki.find().to_list(length=None)
            for бракк in бракк:
                if 'рума до' in бракк:
                    if бракк['рума до'] - time.time() <= 24*60*60 and бракк['рума до'] - time.time() > 0:
                        user1 = self.bot.get_user(бракк['пара']['первый'])
                        user2 = self.bot.get_user(бракк['пара']['второй'])
                        if user1:
                            await user1.send("У вас остался один день любовной румы")
                        if user2:
                            await user2.send("У вас остался один день любовной румы")
                    elif бракк['рума до'] < time.time():
                        if бракк['баланс пары'] >= 2500:
                            await braki.update_one({'_id': бракк['_id']}, {'$set': {'лав рума': True, 'рума до': time.time() + 7*24*60*60, 'баланс пары': бракк['баланс пары'] - 2500}})
                            user1 = self.bot.get_user(бракк['пара']['первый'])
                            user2 = self.bot.get_user(бракк['пара']['второй'])
                            if user1:
                                await user1.send("С вашего баланса списано 2500 монет, рума продлена на 7 дней")
                            if user2:
                                await user2.send("С вашего баланса списано 2500 монет, рума продлена на 7 дней")
                        else:
                            await braki.update_one({'_id': бракк['_id']}, {'$set': {'лав рума': False, 'рума до': None, 'название любовной румы': 'не установлено'}})
            await asyncio.sleep(300)

    @commands.slash_command(name="lprofile", description="Посмотреть любовный профиль")
    async def lprofile(self, interaction: disnake.ApplicationCommandInteraction, member: disnake.Member = None):
        await interaction.response.defer()
        if member is None:
            member = interaction.author
        brake = await braki.find_one({'пара.первый': member.id}) or await braki.find_one({'пара.второй': member.id})
        if not brake:
            await interaction.edit_original_message(content="Пользователь не состоит в браке")
            return
        member1 = self.bot.get_user(brake['пара']['первый']) if brake['пара']['первый'] == member.id else self.bot.get_user(brake['пара']['второй'])
        member2 = self.bot.get_user(brake['пара']['второй']) if brake['пара']['второй'] != member1.id else self.bot.get_user(brake['пара']['первый'])
        embed = disnake.Embed(
            title="**Любовный профиль**",
            description=f"```{member1.name} ♥ {member2.name}```",
            color=member.color
        )
        embed.set_thumbnail(url=member1.display_avatar.url)
        embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
        if brake['лав рума']:
            embed.add_field(name="**Название любовной румы**", value=f"```{brake['название любовной румы']}```", inline=False)
        embed.add_field(name="**Баланс пары**", value=f"```{brake['баланс пары']}```", inline=True)
        embed.add_field(name="**Онлайн пары**", value=f"```{format_time(brake['онлайн пары'])}```", inline=True)
        if member == interaction.author:
            message = await interaction.edit_original_message(embed=embed)
            view = LprofileView(interaction.author, member, message)
            await message.edit(view=view)
        else:
            await interaction.edit_original_message(embed=embed)

def setup(bot):
    bot.add_cog(Lprofile(bot))