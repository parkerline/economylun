import disnake; from disnake.ext import commands; from settings.config import *;
import time
import pymongo; import asyncio; from motor.motor_asyncio import AsyncIOMotorClient; from settings.db import *;


async def remove_absent_members_from_database(bot):
    guild = bot.get_guild(BOT["GUILD_ID"])
    member_ids = [member.id for member in guild.members]
    db_member_ids = [user['айди'] async for user in users.find({})]

    for db_member_id in db_member_ids:
        if db_member_id not in member_ids:
            await users.delete_one({'айди': db_member_id})
            print(f'Удален участник с ID {db_member_id} из базы данных')

async def update_database(bot):
    await asyncio.gather(
        adduser(bot),
        asd(bot)
    )

async def adduser(bot):
    while True:
        guild = bot.get_guild(BOT["GUILD_ID"])
        for member in guild.members:
            if not member.bot and member.id not in [1220134157741461611, 1220134974431428698, 1220135271622906001, 1220135553102647478]:  # Исключение ботов и определенных ID
                await add_member_to_database(member)
        await asyncio.sleep(60)
        await updatesss(bot)
        


async def asd(bot):
    while True:
        await remove_absent_members_from_database(bot)
        await asyncio.sleep(120)
        
async def updatesss(bot):
    guild = bot.get_guild(BOT["GUILD_ID"])
    for member in guild.members:
        if not member.bot and member.id not in [1220134157741461611, 1220134974431428698, 1220135271622906001, 1220135553102647478]:  # Исключение ботов и определенных ID
            await update_user_structure_in_database(member)


async def add_member_to_database(member):
    existing_user = await users.find_one({'айди': member.id})
    if existing_user is None:
        user = {
            'айди': member.id,
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
                'уведомление отправлено': None,
            },
            'история браков': [],
            'транзакции': [],
        }
        await users.insert_one(user)
        print(f'Добавлен участник с ID {member.id} в базу данных')

async def update_user_structure_in_database(member):
    existing_user = await users.find_one({'айди': member.id})
    if existing_user is None:
        user = {
            'айди': member.id,
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
                'уведомление отправлено': None,
            },
            'история браков': [],
            'транзакции': [],
        }
        await users.insert_one(user)
        print(f'Добавлен участник с ID {member.id} в базу данных')
    else:
        user_structure = {
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
                'уведомление отправлено': None,
            },
            'история браков': [],
            'транзакции': [],
        }
        for key, value in user_structure.items():
            if key == 'профиль':
                for sub_key in value:
                    if sub_key not in existing_user[key]:
                        await users.update_one({'айди': member.id}, {'$set': {f'{key}.{sub_key}': value[sub_key]}})
                        print(f'Обновлен участник с ID {member.id} в базе данных')
            elif key not in existing_user:
                await users.update_one({'айди': member.id}, {'$set': {key: value}})
                print(f'Обновлен участник с ID {member.id} в базе данных')