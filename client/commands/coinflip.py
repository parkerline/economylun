import disnake; from disnake.ext import commands; from disnake import *; from disnake.ui import *;
import time; import random;
from settings.config import *; from settings.db import *; from server.conf.emoji import *

class CoinflipView(disnake.ui.View):
    def __init__(self, user, bot, message, ставка):
        super().__init__(timeout=40)
        self.user = user
        self.bot = bot
        self.message = message
        self.ставка = ставка

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if interaction.user != self.user:
            await interaction.response.send_message("Вы не можете использовать эти кнопки, так как не являетесь автором команды.", ephemeral=True)
            return False
        return True
    
    @disnake.ui.button(label="Орёл", style=disnake.ButtonStyle.gray, custom_id="coinflip_heads")
    async def coinflip_heads(self, button: disnake.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer(ephemeral=True)
        user = await users.find_one({'айди': interaction.user.id})
        if user['профиль']['баланс'] < self.ставка:
            await interaction.edit_original_message("У вас недостаточно средств для участия в игре", ephemeral=True)
            return
        embed = disnake.Embed(
            title="**Монетка**",
            description="Вы выбрали **Орёл** монетка подбрасывается...",
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
        await self.message.edit(embed=embed, view=None)
        await asyncio.sleep(3)
        await users.update_one({'айди': interaction.user.id}, {'$inc': {'профиль.баланс': -self.ставка}})
        result = random.choice(['Орёл', 'Решка'])
        if result == 'Орёл':
            await users.update_one({'айди': interaction.user.id}, {'$inc': {'профиль.баланс': self.ставка * 2}})
            embed = disnake.Embed(
                title="**Монетка**",
                description=f"**Вы угадали! Вы выиграли {self.ставка * 2}** {ЭМОДЗИ['money']}",
                color=disnake.Color.green(),
            )
        else:
            embed = disnake.Embed(
                title="**Монетка**",
                description=f"Вы проиграли! Вы потеряли {self.ставка} монет {ЭМОДЗИ['money']}",
                color=disnake.Color.red(),
            )
        embed.add_field(name="**Ваш выбор**", value="Орёл", inline=True)
        embed.add_field(name="**Результат**", value=result, inline=True)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
        await self.message.edit(embed=embed, view=None)

    @disnake.ui.button(label="Решка", style=disnake.ButtonStyle.gray, custom_id="coinflip_tails")
    async def coinflip_tails(self, button: disnake.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer(ephemeral=True)
        user = await users.find_one({'айди': interaction.user.id})
        if user['профиль']['баланс'] < self.ставка:
            await interaction.edit_original_message("У вас недостаточно средств для участия в игре", ephemeral=True)
            return
        embed = disnake.Embed(
            title="**Монетка**",
            description="Вы выбрали **Решка** монетка подбрасывается...",
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
        await self.message.edit(embed=embed, view=None)
        await asyncio.sleep(3)
        await users.update_one({'айди': interaction.user.id}, {'$inc': {'профиль.баланс': -self.ставка}})
        result = random.choice(['Орёл', 'Решка'])
        if result == 'Решка':
            await users.update_one({'айди': interaction.user.id}, {'$inc': {'профиль.баланс': self.ставка * 2}})
            embed = disnake.Embed(
                title="**Монетка**",
                description=f"**Вы угадали! Вы выиграли {self.ставка * 2}** {ЭМОДЗИ['money']}",
                color=disnake.Color.green(),
            )
        else:
            embed = disnake.Embed(
                title="**Монетка**",
                description=f"Вы проиграли! Вы потеряли {self.ставка} монет {ЭМОДЗИ['money']}",
                color=disnake.Color.red(),
            )
        embed.add_field(name="**Ваш выбор**", value="Решка", inline=True)
        embed.add_field(name="**Результат**", value=result, inline=True)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
        await self.message.edit(embed=embed, view=None)

class Coinflip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="coinflip", description="Играть в монетку")
    async def coinflip(self, interaction: disnake.ApplicationCommandInteraction, ставка: int):
        await interaction.response.defer()
        if ставка < 100:
            embed = disnake.Embed(
                title="**Монетка**",
                description=f"Ставка должна быть от **100 монет** {ЭМОДЗИ['money']}",
            )
            embed.set_thumbnail(url=interaction.author.display_avatar.url)
            embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
            embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
            return await interaction.edit_original_message(embed=embed)
        
        user = await users.find_one({'айди': interaction.author.id})
        if user['профиль']['баланс'] < ставка:
            embed = disnake.Embed(
                title="**Монетка**",
                description="У вас недостаточно средств",
            )
            embed.add_field(name="**Ваш баланс**", value=f"```{user['профиль']['баланс']}```")
            embed.add_field(name="**Ваша ставка**", value=f"```{ставка}```")
            embed.set_thumbnail(url=interaction.author.display_avatar.url)
            embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
            embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
            return await interaction.edit_original_message(embed=embed)
        
        embed = disnake.Embed(
            title="**Монетка**",
            description="Выберите сторону монетки",
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
        embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
        message = await interaction.edit_original_message(embed=embed)
        view = CoinflipView(interaction.author, self.bot, message, ставка)
        await message.edit(view=view)

def setup(bot):
    bot.add_cog(Coinflip(bot))