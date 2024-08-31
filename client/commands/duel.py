import disnake; from disnake.ext import commands; from disnake import *; from disnake.ui import *;
import time; import random;
from settings.config import *; from settings.db import *; from server.conf.emoji import *

class DuelView(disnake.ui.View):
    def __init__(self, user, bot, message, ставка):
        super().__init__(timeout=40)  # установите таймаут на 40 секунд
        self.user = user
        self.bot = bot
        self.message = message
        self.ставка = ставка
        self.opponent = None

    @disnake.ui.button(label="Вступить", style=disnake.ButtonStyle.gray)
    async def duel_yes(self, button: disnake.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer(ephemeral=True)
        if interaction.user == self.user:
            await interaction.followup.send("Вы не можете вступить в свою же дуэль")
            return
        self.opponent = interaction.user
        user = await users.find_one({'айди': interaction.user.id}) 
        if user['профиль']['баланс'] < self.ставка:
            await interaction.followup.send("У вас недостаточно средств для участия в дуэли")
            return
        await users.update_one({'айди': interaction.user.id}, {'$inc': {'профиль.баланс': -self.ставка}})
        await users.update_one({'айди': self.user.id}, {'$inc': {'профиль.баланс': -self.ставка}})
        embed = disnake.Embed(
            title="**Дуэль**",
            description=f"{interaction.user.mention} **вступил в дуэль с {self.user.mention} на {self.ставка}** {ЭМОДЗИ['money']} дуэль началась!",
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
        await self.message.edit(embed=embed, view=None)
        await asyncio.sleep(3)
        winner = random.choice([self.user, self.opponent])
        await users.update_one({'айди': winner.id}, {'$inc': {'профиль.баланс': self.ставка * 2}})
        embed = disnake.Embed(
            title="**Дуэль**",
        )
        embed.add_field(name="**Проигравший**", value=self.user.mention if winner == self.opponent else self.opponent.mention, inline=True)
        proigral_money = self.ставка if winner == self.opponent else 0
        embed.add_field(name="**Проиграл**", value=f"{proigral_money} {ЭМОДЗИ['money']}", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.add_field(name="**Выигравший**", value=winner.mention, inline=True)
        embed.add_field(name="**Выигрыш**", value=f"{self.ставка * 2} {ЭМОДЗИ['money']}", inline=True)
        embed.set_thumbnail(url=winner.display_avatar.url)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
        await self.message.edit(embed=embed)


class Duel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="duel", description="Дуэль с другим пользователем")
    async def duel(self, interaction: disnake.ApplicationCommandInteraction, ставка: int):
        await interaction.response.defer()
        if ставка < 100:
            embed = disnake.Embed(
                title="**Дуэль**",
                description="Ставка должна быть от **100 монет**",
            )
            embed.set_thumbnail(url=interaction.author.display_avatar.url)
            embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
            embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
            return await interaction.edit_original_message(embed=embed)
        user = await users.find_one({'айди': interaction.author.id})
        if user['профиль']['баланс'] < ставка:
            embed = disnake.Embed(
                title="**Дуэль**",
                description="У вас недостаточно средств",
            )
            embed.add_field(name="**Ваш баланс**", value=f"```{user['профиль']['баланс']}```")
            embed.add_field(name="**Ваша ставка**", value=f"```{ставка}```")
            embed.set_thumbnail(url=interaction.author.display_avatar.url)
            embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
            embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
            return await interaction.edit_original_message(embed=embed)
        embed = disnake.Embed(
            title="**Дуэль**",
            description=f"{interaction.author.mention} **создал дуэль на {ставка}** {ЭМОДЗИ['money']}",
        )
        embed.set_thumbnail(url=interaction.author.display_avatar.url)
        embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
        embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
        message = await interaction.edit_original_message(embed=embed)
        view = DuelView(interaction.author, self.bot, message, ставка)
        await message.edit(view=view)

def setup(bot):
    bot.add_cog(Duel(bot))