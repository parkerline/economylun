import disnake; from disnake.ext import commands; from disnake import *; from disnake.ui import *; import requests; import textwrap;
import time; import re; import asyncio; import PIL; from PIL import Image, ImageDraw, ImageFont, ImageChops; from io import BytesIO
from settings.config import *; from settings.db import *; from server.conf.emoji import *; from server.conf.cfg import *; import os;
from server.db.dbfunc import *; from server.clandb import *

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_circle_mask(self, image):
        mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + image.size, fill=255)
        return mask

    @commands.slash_command(name="profile", description="Посмотреть профиль пользователя")
    async def profile(self, interaction: disnake.ApplicationCommandInteraction, user: disnake.Member = None):
        await interaction.response.defer()
        embed = disnake.Embed(
            title='Профиль',
            description='Подождите, пока мы обработаем ваш запрос...',
        )
        await interaction.edit_original_response(embed=embed)
        if user is None:
            user = interaction.author
        if user.bot:
            await interaction.response.send_message("Боты не имеют профилей", ephemeral=True)
            return

        user_data = await users.find_one({"айди": user.id})
        balance = user_data['профиль']['баланс']
        online = user_data['профиль']['общий онлайн']
        messages = user_data['профиль']['сообщений']
        rep = user_data['профиль']['репутация']

        image = Image.open('profiles/prof.png')
        resized_image = image.resize((1072, 603))
        draw = ImageDraw.Draw(image)
        font1 = ImageFont.truetype('profiles/pro.ttf', size=30)
        font2 = ImageFont.truetype('profiles/pro.ttf', size=25)
        fontbalance = ImageFont.truetype('profiles/pro.ttf', size=40)

        text1 = f"{user.display_name}"
        bbox = draw.textbbox((0, 0), text1, font=fontbalance)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        new_x1 = 393 - w//2
        draw.text((new_x1, 488), text1, fill='white', font=fontbalance)

        response = requests.get(str(user.display_avatar.url))
        avatar_member = Image.open(BytesIO(response.content))
        avatar_member = avatar_member.resize((int(279), int(279)))
        if avatar_member.mode != 'RGBA':
            avatar_member = avatar_member.convert('RGBA')
        mask_member = self.create_circle_mask(avatar_member)
        mask_member = mask_member.resize(avatar_member.size)
        avatar_member.putalpha(mask_member)
        image.paste(avatar_member, (262, 195), avatar_member)

        text2 = f"{balance}"
        para3 = textwrap.wrap(text2, width=40)
        MAX_W2, MAX_H2 = 1050, 797
        current_h2, pad2 = 797, 10
        for line2 in para3:
            bbox = draw.textbbox((0, 0), line2, font=fontbalance)
            w2, h2 = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((295, current_h2), line2, font=fontbalance)
            current_h2 += h2 + pad2

        seconds = online
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        text3 = f"{hours} ч. {minutes} мин."
        para3 = textwrap.wrap(text3, width=40)
        MAX_W2, MAX_H2 = 1050, 201
        current_h2, pad2 = 201, 10
        for line2 in para3:
            bbox = draw.textbbox((0, 0), line2, font=font1)
            w2, h2 = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((997, current_h2), line2, font=font1)
            current_h2 += h2 + pad2

        marriage_data = await braki.find_one({'$or': [{'пара.первый': user.id}, {'пара.второй': user.id}]})
        if marriage_data:
            if marriage_data['пара']['первый'] == user.id:
                partner_id = marriage_data['пара']['второй']
                partner_role = 'первый'
            else:
                partner_id = marriage_data['пара']['первый']
                partner_role = 'второй'
            partner = self.bot.get_user(partner_id)
            partner_name = partner.display_name if partner else 'Неизвестный пользователь'
            response = requests.get(str(partner.display_avatar.url))
            avatar_partner = Image.open(BytesIO(response.content))
            avatar_partner = avatar_partner.resize((int(122), int(122)))
            if avatar_partner.mode != 'RGBA':
                avatar_partner = avatar_partner.convert('RGBA')
            mask = self.create_circle_mask(avatar_partner)
            avatar_partner.putalpha(mask)
            image.paste(avatar_partner, (1384, 212), avatar_partner)
        else:
            partner_name = 'Нет партнера'
            partner_role = 'Нет роли'

        text4 = f"{partner_name}"
        para3 = textwrap.wrap(text4, width=40)
        MAX_W2, MAX_H2 = 1050, 253
        current_h2, pad2 = 253, 10
        for line2 in para3:
            bbox = draw.textbbox((0, 0), line2, font=font1)
            w2, h2 = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((1518  , current_h2), line2, font=font1)
            current_h2 += h2 + pad2

        user_id = user.id
        rank = await get_online_rank(user)
        text5 = f"{rank}"
        para3 = textwrap.wrap(text5, width=40)
        MAX_W2, MAX_H2 = 1050, 373
        current_h2, pad2 = 373, 10
        for line2 in para3:
            bbox = draw.textbbox((0, 0), line2, font=font1)
            w2, h2 = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((944  , current_h2), line2, font=font1)
            current_h2 += h2 + pad2

        text6 = f"{messages}"
        para3 = textwrap.wrap(text6, width=40)
        MAX_W2, MAX_H2 = 1050, 288
        current_h2, pad2 = 288, 10
        for line2 in para3:
            bbox = draw.textbbox((0, 0), line2, font=font1)
            w2, h2 = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((1057, current_h2), line2, font=font1)
            current_h2 += h2 + pad2

        text7 = f"{rep}"
        para3 = textwrap.wrap(text7, width=40)
        MAX_W2, MAX_H2 = 1050, 462
        current_h2, pad2 = 462, 10
        for line2 in para3:
            bbox = draw.textbbox((0, 0), line2, font=font1)
            w2, h2 = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((1035, current_h2), line2, font=font1)
            current_h2 += h2 + pad2

        clan = await clans_c.find_one({'айди участников': user.id})
        if clan:
            clan_name = clan['название клана']
            clan_member = clan['айди участников']
            clan_deputy = clan['айди заместителей']
            clan_leader = clan['айди лидера']
        else:
            clan_name = 'Нет клана'
            clan_member = []
            clan_deputy = []
            clan_leader = None

        clan_name_font = ImageFont.truetype('profiles/pro.ttf', size=35)
        text8 = f"{clan_name}"
        para3 = textwrap.wrap(text8, width=40)
        MAX_W2, MAX_H2 = 1050, 449
        current_h2, pad2 = 449, 10
        for line2 in para3:
            bbox = draw.textbbox((0, 0), line2, font=clan_name_font)
            w2, h2 = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((1519, current_h2), line2, font=clan_name_font)
            current_h2 += h2 + pad2

        clan_role = 'Лидер' if user.id == clan_leader else 'Заместитель' if user.id in clan_deputy else 'Участник' if user.id in clan_member else 'Нет клана'

        clan_role_font = ImageFont.truetype('profiles/pro.ttf', size=25)
        text9 = f"{clan_role}"
        para3 = textwrap.wrap(text9, width=40)
        MAX_W2, MAX_H2 = 1050, 497  
        current_h2, pad2 = 504, 10
        for line2 in para3:
            bbox = draw.textbbox((0, 0), line2, font=clan_role_font)
            w2, h2 = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((1546, current_h2), line2, font=clan_role_font)
            current_h2 += h2 + pad2

        image_path = f"profiless/{user.id}.png"
        if not os.path.exists('profiless'):
            os.makedirs('profiless')
        
        image.save(image_path)

        await interaction.edit_original_response(embed=None, file=disnake.File(image_path))
        os.remove(image_path)

def setup(bot):
    bot.add_cog(Profile(bot))