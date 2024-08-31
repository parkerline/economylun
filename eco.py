import disnake; from disnake.ext import commands; from settings.config import *;
import os; import logging; import glob;
from server.db.dbstart import *


bot = commands.Bot(
    command_prefix="!",
    test_guilds=[BOT["GUILD_ID"]],
    intents=disnake.Intents.all()
)
base_dir = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger('bot')
file_handler = logging.FileHandler(filename='bot.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(file_handler)

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

async def load_cogs(bot):
    for filename in glob.glob('client/**/*.py', recursive=True):
        if os.path.basename(filename).startswith('_'):
            continue
        extension = filename.replace('/', '.').replace('\\', '.').replace('.py', '')
        try:
            bot.load_extension(extension)
            print(f'Загружено расширение: {extension}')
            logger.info(f'Загружено расширение: {extension}')
        except commands.ExtensionFailed as e:
            print(f'Ошибка при загрузке расширения {extension}: {e.original}')
            logger.error(f'Ошибка при загрузке расширения {extension}: {e.original}')
        except commands.ExtensionNotFound as e:
            print(f'Расширение не найдено: {extension}')
            logger.error(f'Расширение не найдено: {extension}')
        except commands.NoEntryPointError as e:
            print(f'Не найдена точка входа в расширении: {extension}')
            logger.error(f'Не найдена точка входа в расширении: {extension}')
        except commands.ExtensionAlreadyLoaded as e:
            print(f'Расширение уже загружено: {extension}')
            logger.error(f'Расширение уже загружено: {extension}')


@bot.event
async def on_ready():
    print(f"Бот {bot.user.name} успешно запущен и готов к работе!")
    #await bot.http.bulk_upsert_global_commands(bot.user.id, [])
    #for guild_id in bot._test_guilds:
        #await bot.http.bulk_upsert_guild_commands(bot.user.id, guild_id, [])
    await load_cogs(bot)
    await update_database(bot)

bot.run(BOT["TOKEN"])