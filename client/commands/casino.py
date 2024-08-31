import disnake; from disnake.ext import commands; from disnake import *; from disnake.ui import *;
import time; import random;
from settings.config import *; from settings.db import *; from server.conf.emoji import *


class Casino(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="casino", description="Играть в казино")
    async def casino(self, interaction: disnake.ApplicationCommandInteraction, ставка: int):
        await interaction.response.defer()
        embed = disnake.Embed(
            title="**Казино**",
            description="Играем в казино",
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
        embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
        await interaction.edit_original_message(embed=embed)
        await asyncio.sleep(5)
        if ставка < 100:
            embed = disnake.Embed(
                title="**Казино**",
                description=f"Ставка должна быть от **100 монет** {ЭМОДЗИ['money']}",
            )
            embed.set_thumbnail(url=interaction.author.display_avatar.url)
            embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
            embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
            return await interaction.edit_original_message(embed=embed)
        if ставка > 1000:
            embed = disnake.Embed(title='**Казино**', description='Максимальная ставка - 1000 монет').set_thumbnail(url=interaction.author.display_avatar.url).set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url).set_footer(text='Экономика', icon_url=self.bot.user.display_avatar.url)
            return await interaction.edit_original_message(embed=embed)
        user = await users.find_one({'айди': interaction.author.id})
        if user['профиль']['баланс'] < ставка:
            embed = disnake.Embed(
                title="**Казино**",
                description="У вас недостаточно средств",
            )
            embed.add_field(name="**Ваш баланс**", value=f"```{user['профиль']['баланс']}```")
            embed.add_field(name="**Ваша ставка**", value=f"```{ставка}```")
            embed.set_thumbnail(url=interaction.author.display_avatar.url)
            embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
            embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
            return await interaction.edit_original_message(embed=embed)
        await users.update_one({'айди': interaction.author.id}, {'$inc': {'профиль.баланс': -ставка}})
        '''if interaction.author.id == 995032922207821884:
            number = random.randint(50, 100)
        else:
            number = random.randint(0, 100)'''
        number = random.randint(0, 100)
        if number > 50:
            выигрыш = ставка * 2
        elif number == 50:
            выигрыш = ставка * 3
        elif number == 100:
            выигрыш = ставка * 4
        else:
            embed = disnake.Embed(
                title="**Казино**",
                description="Вы проиграли",
                color=disnake.Color.red(),
            )
            embed.add_field(name="**Ваша ставка**", value=f"{ставка} монет {ЭМОДЗИ['money']}")
            embed.add_field(name="**Выпавшее число**", value=f"{number}")
            embed.add_field(name="**Нужное число**", value=f"от 50")
            embed.set_thumbnail(url=interaction.author.display_avatar.url)
            embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
            embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
            return await interaction.edit_original_message(embed=embed)
        await users.update_one({'айди': interaction.author.id}, {'$inc': {'профиль.баланс': выигрыш}})
        embed = disnake.Embed(
            title="**Казино**",
            description="Вы выиграли",
            color=disnake.Color.green(),
        )
        embed.add_field(name="**Ваша ставка**", value=f"{ставка} монет {ЭМОДЗИ['money']}")
        embed.add_field(name="**Выпавшее число**", value=f"{number}")
        embed.add_field(name="**Ваш выигрыш**", value=f"{выигрыш}")
        embed.set_thumbnail(url=interaction.author.display_avatar.url)
        embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
        embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
        await interaction.edit_original_message(embed=embed)

def setup(bot):
    bot.add_cog(Casino(bot))