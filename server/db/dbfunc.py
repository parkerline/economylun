import disnake; from disnake.ext import commands; from settings.config import *;
import time
import pymongo; import asyncio; from motor.motor_asyncio import AsyncIOMotorClient; from settings.db import *

async def get_online_rank(user):
    documents = users.find().sort("профиль.общий онлайн", pymongo.DESCENDING)
    documents = await documents.to_list(None)

    for i, document in enumerate(documents):
        if document['айди'] == user.id:
            return i + 1

    return None