import disnake; from disnake.ext import commands; from settings.config import *;
import time
import pymongo; import asyncio; from motor.motor_asyncio import AsyncIOMotorClient;

client = AsyncIOMotorClient(BOT["MONGO_URI"])
db = client['lunacy']
users = db['users']
shops = db['shop']
braki = db['braki']
paneladmin = db['paneladmin']
profiles = db['users']
privates = db['privates']
donate = db['donate']

async def apanel():
    apanel = {
        'айди': None,
        'выдача монет': 0,
        'выдача звездочек': 0,
    } 
    await paneladmin.insert_one(apanel)
    
async def adonate():
    donate_d = {
        'айди-сервера': None,
        'айди-роли': None,
        'добавил': None,
        'цена': None,
        'купили': [],
    }
    await donate.insert_one(donate_d)

async def brak():
    brakis = {
        'пара': {
            'первый': None,
            'второй': None,
        },
        'баланс пары': 0,
        'онлайн пары': 0,
        'дата': None,
        'статус': 'не установлен',
        'лав рума': False,
        'рума до': None,
        'название любовной румы': 'не установлено',
        'айди румы': None
    }
    await braki.insert_one(brakis)

async def user():
    users = {
        'айди': None,
        'профиль': {
            'баланс': 0,
            'звездочки': 0,
            'опыт': 0,
            'уровень': 1,
            'общий онлайн': 0,
            'онлайн за день': 0,
            'онлайн за неделю': 0,
            'сообщений': 0,
            'статус': 'не установлен',
            'репутация': 0,
            'последнее повышение репутации': None,
        },
        'последний бонус': None,
        'личная рума': {
            'статус': 'неактивно',
            'название': None,
            'айди румы': None,
            'роль': None,
            'активна до': None,
        },
        'история браков': [
            {
                'пара': {
                    'первый': None,
                    'второй': None,
                },
                'дата': None,
            }
        ],
        'транзакции': [
            {
                'отправитель': None,
                'получатель': None,
                'сумма': None,
                'дата': None,
            },
        ],
    }
    await users.insert_one(users)

async def shop():
    shops = {
        'владелец': None,
        'айди роли': None,
        'название': None,
        'цена': None,
        'цвет': None,
        'кол-во покупок': 0,
    }
    await shops.insert_one(shops)

