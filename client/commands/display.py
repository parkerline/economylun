import disnake
from disnake.ext import commands

class Display(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
                
    @commands.slash_command(name="avatar", description="Посмотреть аватар пользователя")
    async def avatar(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member = None):
        if member is None:
            member = inter.author
        embed = disnake.Embed(title=f"Аватар пользователя: {member.display_name}")
        if member.display_avatar.url:
            embed.set_image(url=member.display_avatar.url)
        else:
            embed.description = "У пользователя нет аватарки."
        await inter.response.send_message(embed=embed)
        
    @commands.slash_command(name="baner", description="Посмотреть банер пользователя")
    async def banner(self, inter: disnake.ApplicationCommandInteraction, member: disnake.User = None):
        if member is None:
            member = inter.author
        embed = disnake.Embed(title=f"Баннер пользователя: {member.display_name}")
        user = await self.bot.fetch_user(member.id)
        if user.banner:
            embed.set_image(url=user.banner.url)
        else:
            embed.description = "У пользователя нет баннера."
        await inter.response.send_message(embed=embed)

def setup(bot):
    bot.add_cog(Display(bot))