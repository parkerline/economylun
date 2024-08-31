import disnake; from disnake.ext import commands; from disnake import *; from disnake.ui import *; import requests; import textwrap;
import time; import re; import asyncio; import PIL; from PIL import Image, ImageDraw, ImageFont, ImageChops; from io import BytesIO
from settings.config import *; from settings.db import *; from server.conf.emoji import *; from server.conf.cfg import *; import os;
from server.db.dbfunc import *

db = client["clans"]
clans_c = db["clans"]

async def clane():
    clan_d = {
        'айди сервера': None,
        'айди клана': None,
        'название клана': None,
        'айди лидера': None,
        'айди участников': [],
        'айди заместителей': [],
        'айди роли': None,
        'айди текстового канала': None,
        'айди голосового канала': None,
        'дата создания': time.time(),
        'статистика': {
            'участники': 0,
            'максимум участников': 10,
            'уровень': 0,
            'опыт': 0,
            'рейтинг клана': 0,
            'баланс клана': 0,
            'войны': [],
            'союзы': [],
            'онлайн': {
                'общий онлайн': 0,
                'онлайн за день': 0,
                'онлайн за неделю': 0,
            },
        },
    }
    await clans_c.insert_one(clan_d)