import disnake; from disnake.ext import commands; from disnake import *; from disnake.ui import *;
import time;
from settings.config import *; from settings.db import *; from server.conf.emoji import *

class Transactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="transactions", description="Просмотреть транзакции")
    async def transactions(self, interaction: disnake.ApplicationCommandInteraction, member: disnake.Member = None):
        await interaction.response.defer()
        embed = disnake.Embed(title='Подождите...', description='Идет загрузка данных...', color=0x0080ff)
        msg = await interaction.edit_original_message(embed=embed)
        member = member or interaction.author
        user = await users.find_one({'айди': member.id})
        if user is None:
            await interaction.followup.send("Пользователь не найден", ephemeral=True)
            await msg.delete()
            return
        transactions = user['транзакции']
        if not transactions:
            await interaction.followup.send("Транзакции не найдены", ephemeral=True)
            await msg.delete()
            return
        for transaction in transactions:
            sender = self.bot.get_user(transaction['отправитель'])
            recipient = self.bot.get_user(transaction['получатель'])
            index = transactions.index(transaction) + 1
            if sender is None:
                sender = await self.bot.fetch_user(transaction['отправитель'])
            if recipient is None:
                recipient = await self.bot.fetch_user(transaction['получатель'])
                await interaction.followup.send("Пользователь не найден", ephemeral=True)
                await msg.delete()
                return
        transactions = sorted(transactions, key=lambda x: x['дата'], reverse=True)
        transactions = transactions[:10]
        embed = disnake.Embed(
            title=f"Транзакции пользователя {member.display_name}",
            description=f"{index}) **{sender.mention} — {recipient.mention}** {ЭМОДЗИ['razdelitel']}**Монет** **{transaction['сумма']}** {ЭМОДЗИ['money']}",
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.display_avatar.url)
        embed.set_footer(text=f"Экономика", icon_url=self.bot.user.display_avatar.url)
        await msg.edit(embed=embed)

def setup(bot):
    bot.add_cog(Transactions(bot))