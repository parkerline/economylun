import disnake; from disnake.ext import commands, tasks; from disnake import *; from disnake.ui import *;
import time;
from settings.db import *; from server.conf.cfg import *; 

class ModalName(disnake.ui.Modal):
    def __init__(self, author):
        self.author = author
        self.name = disnake.ui.TextInput(
            label="Название комнаты",
            custom_id="name_in",
            placeholder="Введите название комнаты",
            min_length=1,
            max_length=25,
            required=True,
        )
        super().__init__(title="Изменение названия", components=[self.name])

    async def callback(self, interaction: disnake.MessageInteraction):
        name = interaction.text_values["name_in"]
        await privates.update_one({"владелец": self.author.id}, {"$set": {"название": self.name.value}})
        db = await privates.find_one({"владелец": self.author.id})
        channel_id = db["айди-канала"]
        channel = interaction.guild.get_channel(channel_id)
        await channel.edit(name=f"{name}")
        await interaction.response.send_message(f"Название изменено {name}!", ephemeral=True)

class ModalLimit(disnake.ui.Modal):
    def __init__(self, author):
        self.author = author
        self.limit = disnake.ui.TextInput(
            label="Лимит",
            custom_id="limit_in",
            placeholder="Введите лимит",
            min_length=1,
            max_length=2,
            required=True,
        )
        super().__init__(title="Изменение лимита", components=[self.limit])

    async def callback(self, interaction: disnake.MessageInteraction):
        try:
            limit = int(interaction.text_values["limit_in"])
        except ValueError:
            await interaction.response.send_message("Введите число!", ephemeral=True)
            return
        
        db = await privates.find_one({"владелец": self.author.id})
        channel_id = db["айди-канала"]
        channel = interaction.guild.get_channel(channel_id)
        await channel.edit(user_limit=limit)
        await interaction.response.send_message(f"Лимит изменен на {limit}!", ephemeral=True)

class UserTakeView(disnake.ui.View):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.add_item(UserTake(user))

class UserTake(disnake.ui.UserSelect):
    def __init__(self, user):
        self.user = user
        super().__init__(placeholder="Выберите пользователя", min_values=1, max_values=1)

    async def callback(self, interaction: disnake.MessageInteraction):
        db = await privates.find_one({"владелец": self.user.id})
        channel_id = db["айди-канала"]
        channel = interaction.guild.get_channel(channel_id)
        member_id = interaction.data['values'][0]
        member = interaction.guild.get_member(int(member_id))
        if member is None:
            await interaction.response.send_message("Пользователь не найден!", ephemeral=True)
            return
        if member == self.user:
            await interaction.response.send_message("Вы не можете забрать доступ у себя!", ephemeral=True)
            return
        if member not in interaction.guild.members:
            await interaction.response.send_message("Пользователь не в гильдии!", ephemeral=True)
            return
        permissions = channel.overwrites_for(member)
        if permissions.connect is False:
            await interaction.response.send_message("У пользователя уже забран доступ!", ephemeral=True)
            return
        await channel.set_permissions(member, connect=False)
        await interaction.response.send_message(f"Пользователю {member.mention} забран доступ к каналу!", ephemeral=True)

class UserGiveView(disnake.ui.View):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.add_item(UserGive(user))

class UserGive(disnake.ui.UserSelect):
    def __init__(self, user):
        self.user = user
        super().__init__(placeholder="Выберите пользователя", min_values=1, max_values=1)

    async def callback(self, interaction: disnake.MessageInteraction):
        db = await privates.find_one({"владелец": self.user.id})
        channel_id = db["айди-канала"]
        channel = interaction.guild.get_channel(channel_id)
        member_id = interaction.data['values'][0]
        member = interaction.guild.get_member(int(member_id))
        if member is None:
            await interaction.response.send_message("Пользователь не найден!", ephemeral=True)
            return
        if member == self.user:
            await interaction.response.send_message("Вы не можете дать доступ себе!", ephemeral=True)
            return
        if member not in interaction.guild.members:
            await interaction.response.send_message("Пользователь не в гильдии!", ephemeral=True)
            return
        permissions = channel.overwrites_for(member)
        if permissions.connect is True:
            await interaction.response.send_message("У пользователя уже есть доступ!", ephemeral=True)
            return
        await channel.set_permissions(member, connect=True)
        await interaction.response.send_message(f"Пользователю {member.mention} дан доступ к каналу!", ephemeral=True)

class UserKickView(disnake.ui.View):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.add_item(UserKick(user))
        
class UserKick(disnake.ui.UserSelect):
    def __init__(self, user):
        self.user = user
        super().__init__(placeholder="Выберите пользователя", min_values=1, max_values=1)
    
    async def callback(self, interaction: disnake.MessageInteraction):
        db = await privates.find_one({"владелец": self.user.id})
        channel_id = db["айди-канала"]
        channel = interaction.guild.get_channel(channel_id)
        member_id = interaction.data['values'][0]
        member = interaction.guild.get_member(int(member_id))
        if member is None:
            await interaction.response.send_message("Пользователь не найден!", ephemeral=True)
            return
        if member == self.user:
            await interaction.response.send_message("Вы не можете выгнать себя!", ephemeral=True)
            return
        if member not in interaction.guild.members:
            await interaction.response.send_message("Пользователь не в гильдии!", ephemeral=True)
            return
        if member.voice is None or member.voice.channel != channel:
            await interaction.response.send_message("Пользователь не в вашем канале!", ephemeral=True)
            return
        await member.move_to(None)
        await interaction.response.send_message(f"Пользователь {member.mention} выгнан из канала!", ephemeral=True)

class UserMuteView(disnake.ui.View):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.add_item(UserMute(user))

class UserMute(disnake.ui.UserSelect):
    def __init__(self, user):
        self.user = user
        super().__init__(placeholder="Выберите пользователя", min_values=1, max_values=1)

    async def callback(self, interaction: disnake.MessageInteraction):
        db = await privates.find_one({"владелец": self.user.id})
        channel_id = db["айди-канала"]
        channel = interaction.guild.get_channel(channel_id)
        member_id = interaction.data['values'][0]
        member = interaction.guild.get_member(int(member_id))
        if member is None:
            await interaction.response.send_message("Пользователь не найден!", ephemeral=True)
            return
        if member == self.user:
            await interaction.response.send_message("Вы не можете замутить себя!", ephemeral=True)
            return
        if member not in interaction.guild.members:
            await interaction.response.send_message("Пользователь не в гильдии!", ephemeral=True)
            return
        if member.voice is None or member.voice.channel != channel:
            await interaction.response.send_message("Пользователь не в вашем канале!", ephemeral=True)
            return
        permissions = channel.overwrites_for(member)
        if permissions.speak is False:
            await interaction.response.send_message("У пользователя уже нет права говорить!", ephemeral=True)
            return
        await channel.set_permissions(member, connect=True, speak=False)
        await member.move_to(None)
        await interaction.response.send_message(f"Пользователю {member.mention} забрано право говорить!", ephemeral=True)

class UserUnmuteView(disnake.ui.View):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.add_item(UserUnmute(user))

class UserUnmute(disnake.ui.UserSelect):
    def __init__(self, user):
        self.user = user
        super().__init__(placeholder="Выберите пользователя", min_values=1, max_values=1)

    async def callback(self, interaction: disnake.MessageInteraction):
        db = await privates.find_one({"владелец": self.user.id})
        channel_id = db["айди-канала"]
        channel = interaction.guild.get_channel(channel_id)
        member_id = interaction.data['values'][0]
        member = interaction.guild.get_member(int(member_id))
        if member is None:
            await interaction.response.send_message("Пользователь не найден!", ephemeral=True)
            return
        if member == self.user:
            await interaction.response.send_message("Вы не можете замутить себя!", ephemeral=True)
            return
        if member not in interaction.guild.members:
            await interaction.response.send_message("Пользователь не в гильдии!", ephemeral=True)
            return
        if member.voice is None or member.voice.channel != channel:
            await interaction.response.send_message("Пользователь не в вашем канале!", ephemeral=True)
            return
        permissions = channel.overwrites_for(member)
        if permissions.speak is True:
            await interaction.response.send_message("У пользователя уже есть права говорить!", ephemeral=True)
            return
        await channel.set_permissions(member, connect=True, speak=True)
        await member.move_to(None)
        await interaction.response.send_message(f"Пользователю {member.mention} забрано право говорить!", ephemeral=True)

class NewPrivate(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label='📝', style=ButtonStyle.gray)
    async def change_name(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        existing_channel = await privates.find_one({"владелец": interaction.user.id})
        if not existing_channel:
            await interaction.response.send_message("У вас нет приватного канала.", ephemeral=True)
            return
        channel_id = existing_channel["айди-канала"]
        channel = interaction.guild.get_channel(channel_id)
        if interaction.user.voice is None or interaction.user.voice.channel != channel:
            await interaction.response.send_message("Вы должны находиться в своем приватном канале, чтобы закрыть его.", ephemeral=True)
            return
        modal = ModalName(interaction.user)
        await interaction.response.send_modal(modal)
        

    @disnake.ui.button(label='✏️', style=ButtonStyle.gray)
    async def change_limit(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        existing_channel = await privates.find_one({"владелец": interaction.user.id})
        if not existing_channel:
            await interaction.response.send_message("У вас нет приватного канала.", ephemeral=True)
            return
        channel_id = existing_channel["айди-канала"]
        channel = interaction.guild.get_channel(channel_id)
        if interaction.user.voice is None or interaction.user.voice.channel != channel:
            await interaction.response.send_message("Вы должны находиться в своем приватном канале, чтобы закрыть его.", ephemeral=True)
            return
        modal = ModalLimit(interaction.user)
        await interaction.response.send_modal(modal)
        
    @disnake.ui.button(label='🔒', style=ButtonStyle.gray)
    async def close_room(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        existing_channel = await privates.find_one({"владелец": interaction.user.id})
        if not existing_channel:
            await interaction.response.send_message("У вас нет приватного канала.", ephemeral=True)
            return
        channel_id = existing_channel["айди-канала"]
        channel = interaction.guild.get_channel(channel_id)
        if interaction.user.voice is None or interaction.user.voice.channel != channel:
            await interaction.response.send_message("Вы должны находиться в своем приватном канале, чтобы закрыть его.", ephemeral=True)
            return
        permissions = channel.overwrites_for(interaction.guild.default_role)
        if permissions.connect is False and permissions.view_channel is False:
            await interaction.response.send_message("Канал уже закрыт и невиден.", ephemeral=True)
            return
        await channel.set_permissions(interaction.guild.default_role, view_channel=False, connect=True)
        await interaction.response.send_message("Канал закрыт для всех!", ephemeral=True)

    @disnake.ui.button(label='🔓', style=ButtonStyle.gray)
    async def open_room(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        existing_channel = await privates.find_one({"владелец": interaction.user.id})
        if not existing_channel:
            await interaction.response.send_message("У вас нет приватного канала.", ephemeral=True)
            return
        channel_id = existing_channel["айди-канала"]
        channel = interaction.guild.get_channel(channel_id)
        if interaction.user.voice is None or interaction.user.voice.channel != channel:
            await interaction.response.send_message("Вы должны находиться в своем приватном канале, чтобы закрыть его.", ephemeral=True)
            return
        permissions = channel.overwrites_for(interaction.guild.default_role)
        if permissions.connect is True and permissions.view_channel is True:
            await interaction.response.send_message("Канал уже открыт и виден.", ephemeral=True)
            return
        await channel.set_permissions(interaction.guild.default_role, view_channel=True, connect=True)
        await interaction.response.send_message("Канал открыт для всех!", ephemeral=True)

    @disnake.ui.button(label='🚫', style=ButtonStyle.gray)
    async def take_access(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        existing_channel = await privates.find_one({"владелец": interaction.user.id})
        if not existing_channel:
            await interaction.response.send_message("У вас нет приватного канала.", ephemeral=True)
            return
        channel_id = existing_channel["айди-канала"]
        channel = interaction.guild.get_channel(channel_id)
        if interaction.user.voice is None or interaction.user.voice.channel != channel:
            await interaction.response.send_message("Вы должны находиться в своем приватном канале, чтобы закрыть его.", ephemeral=True)
            return
        select = UserTakeView(interaction.user)
        await interaction.response.send_message("Выберите пользователя, которому хотите забрать доступ.", view=select, ephemeral=True)
        

    @disnake.ui.button(label='🔑', style=ButtonStyle.gray)
    async def give_access(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        existing_channel = await privates.find_one({"владелец": interaction.user.id})
        if not existing_channel:
            await interaction.response.send_message("У вас нет приватного канала.", ephemeral=True)
            return
        channel_id = existing_channel["айди-канала"]
        channel = interaction.guild.get_channel(channel_id)
        if interaction.user.voice is None or interaction.user.voice.channel != channel:
            await interaction.response.send_message("Вы должны находиться в своем приватном канале, чтобы закрыть его.", ephemeral=True)
            return
        select = UserGiveView(interaction.user)
        await interaction.response.send_message("Выберите пользователя, которому хотите дать доступ.", view=select, ephemeral=True)

    @disnake.ui.button(label='❌', style=ButtonStyle.gray)
    async def kick_user(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        existing_channel = await privates.find_one({"владелец": interaction.user.id})
        if not existing_channel:
            await interaction.response.send_message("У вас нет приватного канала.", ephemeral=True)
            return
        channel_id = existing_channel["айди-канала"]
        channel = interaction.guild.get_channel(channel_id)
        if interaction.user.voice is None or interaction.user.voice.channel != channel:
            await interaction.response.send_message("Вы должны находиться в своем приватном канале, чтобы закрыть его.", ephemeral=True)
            return
        select = UserKickView(interaction.user)
        await interaction.response.send_message("Выберите пользователя, которого хотите выгнать.", view=select, ephemeral=True)

    @disnake.ui.button(label='🔇', style=ButtonStyle.gray)
    async def mute_user(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        existing_channel = await privates.find_one({"владелец": interaction.user.id})
        if not existing_channel:
            await interaction.response.send_message("У вас нет приватного канала.", ephemeral=True)
            return
        channel_id = existing_channel["айди-канала"]
        channel = interaction.guild.get_channel(channel_id)
        if interaction.user.voice is None or interaction.user.voice.channel != channel:
            await interaction.response.send_message("Вы должны находиться в своем приватном канале, чтобы закрыть его.", ephemeral=True)
            return
        select = UserMuteView(interaction.user)
        await interaction.response.send_message("Выберите пользователя, которого хотите замутить.", view=select, ephemeral=True)

    @disnake.ui.button(label='🔊', style=ButtonStyle.gray)
    async def unmute_user(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        existing_channel = await privates.find_one({"владелец": interaction.user.id})
        if not existing_channel:
            await interaction.response.send_message("У вас нет приватного канала.", ephemeral=True)
            return
        channel_id = existing_channel["айди-канала"]
        channel = interaction.guild.get_channel(channel_id)
        if interaction.user.voice is None or interaction.user.voice.channel != channel:
            await interaction.response.send_message("Вы должны находиться в своем приватном канале, чтобы закрыть его.", ephemeral=True)
            return
        select = UserUnmuteView(interaction.user)
        await interaction.response.send_message("Выберите пользователя, которого хотите размутить.", view=select, ephemeral=True)


class Privatki(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.clean_channel_on_start())
        self.check_empty_channels.start()
        self.clean_untracked_channels.start()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel and after.channel.id == ПРИВАТКИ['создать']:
            existing_channel = await privates.find_one({"владелец": member.id})
            if existing_channel:
                channel = self.bot.get_channel(existing_channel["айди-канала"])
                if channel:
                    await member.move_to(channel)
                    return

            category = self.bot.get_channel(ПРИВАТКИ['категория'])
            overwrites = {
                member.guild.default_role: disnake.PermissionOverwrite(view_channel=False, connect=False),
                member: disnake.PermissionOverwrite(connect=True)
            }
            for role_id in РУМЫ['запрет']:
                role = member.guild.get_role(role_id)
                if role:
                    overwrites[role] = disnake.PermissionOverwrite(view_channel=False, connect=False)

            channel = await category.create_voice_channel(f"🔑・ Канал {member.display_name}", overwrites=overwrites)
            await channel.set_permissions(member.guild.default_role, connect=False)
            await channel.set_permissions(member, connect=True)
            await privates.insert_one({"владелец": member.id, "айди-канала": channel.id, "открыт": False})

            await member.move_to(channel)

    async def clean_channel_on_start(self):
        emoji1 = "📝"  # изменить название
        emoji2 = "✏️"  # лимит
        emoji3 = "🔒"  # закрыть комнату
        emoji4 = "🔓"  # открыть комнату
        emoji5 = "🚫"  # забрать доступ
        emoji6 = "🔑"  # выдать доступ
        emoji7 = "❌"  # выгнать из комнаты
        emoji8 = "🔇"  # забрать право говорить
        emoji9 = "🔊"  # выдать право говорить
        await self.bot.wait_until_ready()
        await asyncio.sleep(2)
        channel = self.bot.get_channel(ПРИВАТКИ['настройка'])
        if channel is not None:
            await channel.purge()
            embed = disnake.Embed(title="Управление приватной комнатой", description =f"{emoji1} — изменить **название** комнаты.\n{emoji2} — изменить **лимит** пользователей в комнате.\n{emoji3} — **закрыть** комнату для всех.\n{emoji4} — **открыть** комнату для всех.\n{emoji5} — **забрать** доступ к комнате у пользователя.\n{emoji6} — **выдать** доступ в комнату пользователю.\n{emoji7} — **выгнать** пользователя из комнаты.\n{emoji8} — **забрать** право говорить.\n{emoji9} — **выдать** право говорить.\n")
            view = NewPrivate()
            await channel.send(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == ПРИВАТКИ['настройка'] and not message.author.bot:
            await message.delete()

    @tasks.loop(seconds=7)
    async def check_empty_channels(self):
        category = self.bot.get_channel(ПРИВАТКИ['категория'])
        for channel in category.voice_channels:
            if channel.id != ПРИВАТКИ['создать']:
                doc = await privates.find_one({"айди-канала": channel.id})
                if doc and not channel.members:
                    await channel.delete()
                    await privates.delete_one({"_id": doc["_id"]})


    @tasks.loop(seconds=70)
    async def clean_untracked_channels(self):
        category = self.bot.get_channel(ПРИВАТКИ['категория'])
        for channel in category.voice_channels:
            if channel.id != ПРИВАТКИ['создать']:
                doc = await privates.find_one({"айди-канала": channel.id})
                if not doc and not channel.members:
                    await channel.delete()
                    await privates.delete_one({"айди-канала": channel.id})

        all_docs = await privates.find({}).to_list(length=100)
        for doc in all_docs:
            channel = self.bot.get_channel(doc["айди-канала"])
            if not channel:
                await privates.delete_one({"_id": doc["_id"]})

    @check_empty_channels.before_loop
    async def before_check_empty_channels(self):
        await self.bot.wait_until_ready()

    @clean_untracked_channels.before_loop
    async def before_clean_untracked_channels(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(Privatki(bot))