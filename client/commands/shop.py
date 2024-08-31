import disnake; from disnake.ext import commands; from disnake import *; from disnake.ui import *;
import time; import re;
from settings.config import *; from settings.db import *; from server.conf.emoji import *; from server.conf.cfg import *

class NextButton(disnake.ui.Button):
    def __init__(self, shop_view):
        super().__init__(style=disnake.ButtonStyle.gray, label="Следующая страница", custom_id="next_button")
        self.shop_view = shop_view
        self.disabled = len(self.shop_view.shop) <= 5

    async def callback(self, interaction: disnake.MessageInteraction):
        if interaction.user.id != self.shop_view.user.id:
            await interaction.response.send_message("Вы не можете просматривать магазин другого пользователя", ephemeral=True)
            return
        if (self.shop_view.current_page + 1) * 2 < len(self.shop_view.shop):
            self.shop_view.current_page += 1
            self.shop_view.prev_button.disabled = False
            self.shop_view.buy_select.update_options()
            if (self.shop_view.current_page + 1) * 2 >= len(self.shop_view.shop):
                self.disabled = True
            await interaction.response.edit_message(embed=await self.shop_view.get_embed(), view=self.shop_view)


class PrevButton(disnake.ui.Button):
    def __init__(self, shop_view):
        super().__init__(style=disnake.ButtonStyle.gray, label="Предыдущая страница", custom_id="prev_button")
        self.shop_view = shop_view
        self.disabled = True

    async def callback(self, interaction: disnake.MessageInteraction):
        if interaction.user.id != self.shop_view.user.id:
            await interaction.response.send_message("Вы не можете просматривать магазин другого пользователя", ephemeral=True)
            return
        if self.shop_view.current_page - 1 >= 0:
            self.shop_view.current_page -= 1
            self.shop_view.next_button.disabled = False
            self.shop_view.buy_select.update_options()
            if self.shop_view.current_page - 1 < 0:
                self.disabled = True
            await interaction.response.edit_message(embed=await self.shop_view.get_embed(), view=self.shop_view)


class BuySelect(disnake.ui.Select):
    def __init__(self, shop_view):
        self.shop_view = shop_view
        options = self.shop_view.get_options()
        super().__init__(placeholder="Выберите роль", options=options, custom_id="buy_select")

    def update_options(self):
        self.options = self.shop_view.get_options()

    async def callback(self, interaction: disnake.MessageInteraction):
        if interaction.user.id != self.shop_view.user.id:
            await interaction.response.send_message("Вы не можете купить роль другого пользователя", ephemeral=True)
            return
        role_id = int(interaction.data['values'][0])
        role = await shops.find_one({'айди роли': role_id})
        owner = self.shop_view.bot.get_user(role['владелец'])
        if role_id in [role.id for role in interaction.user.roles]:
            return await interaction.response.send_message("У вас уже есть эта роль", ephemeral=True)

        user = await users.find_one({'айди': interaction.author.id})
        if user['профиль']['баланс'] < role['цена']:
            return await interaction.response.send_message("У вас недостаточно средств для покупки роли", ephemeral=True)
        seller_share = round(role['цена'] * 0.4)
        owner_embed = disnake.Embed(
            title="Ваша роль была куплена",
            description=f"Ваша роль {role['название']} была куплена пользователем {interaction.author.mention}\n"
                        f"Вам начислено {seller_share} {ЭМОДЗИ['money']}"
        )
        # Проверка, открыт ли DM канал с пользователем
        try:
            await owner.send(embed=owner_embed)
        except disnake.errors.Forbidden:
            # Если сообщение не может быть отправлено, можно обработать это здесь
            pass

        await users.update_one({'айди': role['владелец']}, {'$inc': {'профиль.баланс': seller_share}})
        await users.update_one({'айди': interaction.author.id}, {'$inc': {'профиль.баланс': -role['цена']}})
        await shops.update_one({'айди роли': role_id}, {'$inc': {'кол-во покупок': 1}})
        await interaction.author.add_roles(disnake.Object(role_id))
        await interaction.response.send_message(f"Вы успешно купили роль {role['название']}", ephemeral=True)

class ShopView(View):
    def __init__(self, bot, shop, interaction, user):
        super().__init__()
        self.bot = bot
        self.shop = shop
        self.user = user
        self.current_page = 0
        self.interaction = interaction

        self.next_button = NextButton(self)
        self.prev_button = PrevButton(self)
        self.buy_select = BuySelect(self)

        self.add_item(self.prev_button)
        self.add_item(self.buy_select)
        self.add_item(self.next_button)

    def get_options(self):
        options = []
        start = self.current_page * 5
        end = start + 5
        for role in self.shop[start:end]:
            options.append(disnake.SelectOption(label=role['название'], value=str(role['айди роли'])))
        return options[:25]

    async def get_embed(self):
        start = self.current_page * 5
        end = start + 5
        roles = self.shop[start:end]

        description = ""
        for index, role in enumerate(roles, start=start+1):
            role_mention = f"<@&{role['айди роли']}>"
            seller_mention = f"<@{role['владелец']}>"
            description += f"{index}) {role_mention}\nПродавец: {seller_mention}\nЦена: {role['цена']}\nКуплена раз: {role['кол-во покупок']}\n\n"

        embed = disnake.Embed(title="**Магазин ролей**", description=description)
        embed.set_thumbnail(url=self.interaction.author.display_avatar.url)
        embed.set_author(name=self.interaction.author.display_name, icon_url=self.interaction.author.display_avatar.url)
        embed.set_footer(text=f"Экономика | Страница {self.current_page + 1}", icon_url=self.interaction.bot.user.display_avatar.url)
        return embed
    

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.slash_command(name="shop", description="Магазин ролей")
    async def shop(self, interaction: disnake.ApplicationCommandInteraction):
        shop = await shops.find().to_list(None)
        if not shop:
            return await interaction.response.send_message("Магазин пуст", ephemeral=True)
        
        view = ShopView(self.bot, shop, interaction, interaction.user)
        embed = await view.get_embed()
        await interaction.response.send_message(embed=embed, view=view)

def setup(bot):
    bot.add_cog(Shop(bot))