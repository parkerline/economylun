import disnake; from disnake.ext import commands; from disnake import *; from disnake.ui import *; import requests; import textwrap;
import time; import re; import asyncio; import PIL; from PIL import Image, ImageDraw, ImageFont, ImageChops; from io import BytesIO
from settings.config import *; from settings.db import *; from server.conf.emoji import *; from server.conf.cfg import *; import os;
from server.db.dbfunc import *

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

class Divorce(disnake.ui.View):
    def __init__(self, user, member):
        super().__init__(timeout=None)
        self.user = user
        self.member = member
    
    @disnake.ui.button(label="Да", style=disnake.ButtonStyle.green, custom_id="yes")
    async def yes(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        brake = await braki.find_one({'пара.первый': self.user.id}) or await braki.find_one({'пара.второй': self.user.id})
        if not brake:
            await interaction.response.send_message("Вы не состоите в браке", ephemeral=True)
            return
        if brake['пара']['первый'] != self.user.id and brake['пара']['второй'] != self.user.id:
            await interaction.response.send_message("Вы не состоите в браке", ephemeral=True)
            return
        await braki.delete_one({'_id': brake['_id']})
        embed = disnake.Embed(title='Расторжение брака', description='Вы успешно расторгли брак').set_thumbnail(url=self.user.display_avatar.url).set_author(name=self.user.display_name, icon_url=self.user.display_avatar.url)
        await interaction.edit_original_message(embed=embed, view=None)

    @disnake.ui.button(label="Нет", style=disnake.ButtonStyle.red, custom_id="no")
    async def no(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        embed = disnake.Embed(title='Расторжение брака', description='Вы отменили расторжение брака').set_thumbnail(url=self.user.display_avatar.url).set_author(name=self.user.display_name, icon_url=self.user.display_avatar.url)
        await interaction.edit_original_message(embed=embed, view=None)

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
        if brake['баланс пары'] < 2499:
            await interaction.response.send_message("У вас недостаточно средств для покупки", ephemeral=True)
            return
        await braki.update_one({'_id': brake['_id']}, {'$set': {'лав рума': True, 'рума до': time.time() + 7*24*60*60, 'баланс пары': brake['баланс пары'] - 2499}})
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

    @disnake.ui.button(label="Расторгнуть брак", style=disnake.ButtonStyle.red, custom_id="divorce")
    async def divorce(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        embed = disnake.Embed(title='Расторжение брака', description='Вы уверены, что хотите расторгнуть брак?').set_thumbnail(url=self.user.display_avatar.url).set_author(name=self.user.display_name, icon_url=self.user.display_avatar.url)
        view = Divorce(self.user, self.member)
        await interaction.edit_original_message(embed=embed, view=view)

class LProfile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.loveroom_check())

    async def loveroom_check(self):
        while True:
            бракк = await braki.find().to_list(length=None)
            for бракк in бракк:
                if 'рума до' in бракк:
                    if бракк['рума до'] - time.time() <= 24*60*60 and бракк['рума до'] - time.time() > 0:
                        if not бракк.get('уведомление отправлено', False):
                            user1 = self.bot.get_user(бракк['пара']['первый'])
                            user2 = self.bot.get_user(бракк['пара']['второй'])
                            if user1:
                                try:
                                    await user1.send("У вас остался один день любовной румы")
                                except disnake.Forbidden:
                                    pass
                            if user2:
                                try:
                                    await user2.send("У вас остался один день любовной румы")
                                except disnake.Forbidden:
                                    pass
                            await braki.update_one({'_id': бракк['_id']}, {'$set': {'уведомление отправлено': True}})
                    elif бракк['рума до'] < time.time():
                        if бракк['баланс пары'] >= 1500:
                            await braki.update_one({'_id': бракк['_id']}, {'$set': {'лав рума': True, 'рума до': time.time() + 7*24*60*60, 'баланс пары': бракк['баланс пары'] - 2500, 'уведомление отправлено': False}})
                            user1 = self.bot.get_user(бракк['пара']['первый'])
                            user2 = self.bot.get_user(бракк['пара']['второй'])
                            if user1:
                                try:
                                    await user1.send("С вашего баланса списано 1500 монет, рума продлена на 7 дней")
                                except disnake.Forbidden:
                                    pass
                            if user2:
                                try:
                                    await user2.send("С вашего баланса списано 1500 монет, рума продлена на 7 дней")
                                except disnake.Forbidden:
                                    pass
                        else:
                            await braki.update_one({'_id': бракк['_id']}, {'$set': {'лав рума': False, 'рума до': None, 'название любовной румы': 'не установлено', 'уведомление отправлено': False}})
            await asyncio.sleep(300)

    def create_circle_mask(self, image):
        mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + image.size, fill=255)
        return mask
    
    @commands.slash_command(name="lprofile", description="Посмотреть любовный профиль")
    async def lprofile(self, interaction: disnake.ApplicationCommandInteraction, member: disnake.Member = None):
        await interaction.response.defer()
        embed = disnake.Embed(
            title='Профиль',
            description='Подождите, пока мы обработаем ваш запрос...',
        )
        await interaction.edit_original_response(embed=embed)
        if member is None:
            member = interaction.author

        marriage = await braki.find_one({"$or": [{"пара.первый": member.id}, {"пара.второй": member.id}]})
        if marriage is not None:
            if marriage['пара']['первый'] == member.id:
                partner_id = marriage['пара']['второй']  # участник является первым в паре
            elif marriage['пара']['второй'] == member.id:
                partner_id = marriage['пара']['первый']  # участник является вторым в паре
            else:
                pass
        else:
            embed = disnake.Embed(
                title='Профиль',
                description='У вас нет брака',
            )
            await interaction.edit_original_response(embed=embed)
            return

        partner = await self.bot.fetch_user(partner_id)

        if marriage['дата']:
            t = time.localtime(marriage['дата'])
            datamarry = f"{t.tm_mday}.{t.tm_mon}.{t.tm_year}"
        else:
            datamarry = None
        balancepara = marriage['баланс пары']
        onlinemarry = marriage['онлайн пары']
        seconds = onlinemarry
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60

        image = Image.open('profiles/loveprof.png')
        draw = ImageDraw.Draw(image)
        font1 = ImageFont.truetype('profiles/pro.ttf', size=55)
        font2 = ImageFont.truetype('profiles/pro.ttf', size=round(35.28))

        text1 = f"{member.display_name}"
        parts = [text1[i:i+15] for i in range(0, len(text1), 10)]
        for i, part in enumerate(parts):
            bbox = draw.textbbox((0, 0), part, font=font1)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            new_x1 = 384 - w//2
            y = 468 + i*55
            draw.text((new_x1, y), part, fill='white', font=font1)

        response_member = requests.get(str(member.display_avatar.url))
        avatar_member = Image.open(BytesIO(response_member.content))
        avatar_member = avatar_member.resize((int(278), int(278)))
        if avatar_member.mode != 'RGBA':
            avatar_member = avatar_member.convert('RGBA')
        mask_member = self.create_circle_mask(avatar_member)
        mask_member = mask_member.resize(avatar_member.size)
        avatar_member.putalpha(mask_member)
        image.paste(avatar_member, (263, 177), avatar_member)

        text2 = f"{partner.display_name}"
        parts = [text2[i:i+15] for i in range(0, len(text2), 10)]
        for i, part in enumerate(parts):
            bbox = draw.textbbox((0, 0), part, font=font1)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            new_x1 = 1519 - w//2
            y = 468 + i*55
            draw.text((new_x1, y), part, fill='white', font=font1)

        partner = await self.bot.fetch_user(partner_id)
        response_partner = requests.get(str(partner.display_avatar.url))
        avatar_partner = Image.open(BytesIO(response_partner.content))
        avatar_partner = avatar_partner.resize((int(278), int(278)))
        if avatar_partner.mode != 'RGBA':
            avatar_partner = avatar_partner.convert('RGBA')
        mask_partner = self.create_circle_mask(avatar_partner)
        mask_partner = mask_partner.resize(avatar_partner.size)
        avatar_partner.putalpha(mask_partner)
        image.paste(avatar_partner, (1381, 177), avatar_partner)

        text3 = f"{balancepara}"
        para3 = textwrap.wrap(text3, width=40)
        MAX_W2, MAX_H2 = 1050, 873
        current_h2, pad2 = 873, 10
        for line2 in para3:
            bbox = draw.textbbox((0, 0), line2, font=font2)
            w2, h2 = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((402, current_h2), line2, font=font2)
            current_h2 += h2 + pad2

        text4 = f"{hours} ч. {minutes} мин."
        para3 = textwrap.wrap(text4, width=40)
        MAX_W2, MAX_H2 = 1050, 873
        current_h2, pad2 = 873, 10
        for line2 in para3:
            bbox = draw.textbbox((0, 0), line2, font=font2)
            w2, h2 = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((911, current_h2), line2, font=font2)
            current_h2 += h2 + pad2

        text5 = f"{datamarry}"
        para3 = textwrap.wrap(text5, width=40)
        MAX_W2, MAX_H2 = 1050, 873
        current_h2, pad2 = 873, 10
        for line2 in para3:
            bbox = draw.textbbox((0, 0), line2, font=font2)
            w2, h2 = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((1505, current_h2), line2, font=font2)
            current_h2 += h2 + pad2

        image_path = f"profiless/{member.id}.png"
        if not os.path.exists('profiless'):
            os.makedirs('profiless')
        
        image.save(image_path)

        if member == interaction.author:
            message = await interaction.edit_original_response(embed=None, file=disnake.File(image_path))
            view = LprofileView(member, member, message)
            await message.edit(view=view)
        else:
            await interaction.edit_original_response(embed=None, file=disnake.File(image_path))
        
        os.remove(image_path)

def setup(bot):
    bot.add_cog(LProfile(bot))