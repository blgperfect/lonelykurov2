import discord
from discord.ext import commands
import motor.motor_asyncio
from dotenv import load_dotenv
import os
from utils.rank_card import generate_rank_card
import datetime

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DATABASE_NAME]
user_collection = db["users"]

# Salon d'annonce des level ups / succès
ANNOUNCE_CHANNEL_ID = 1357131836601536512
XP_PER_MESSAGE = 10

# Rôles à attribuer par niveau
LEVEL_ROLES = {
    1: 1359707224255107312,
    5: 1359707497107165336,
    15: 1359707724170137680,
    25: 1359707998490071190,
    50: 1359708925082992880,
    70: 1359709378357231646,
    100: 1359709836908036257,
}

# Liste des succès à détecter
SUCCESS_LIST = [
    {"name": "💬 Réactif", "key": "reactions", "target": 50},
    {"name": "🤯 Fan de réact", "key": "reactions", "target": 800},
    {"name": "🚀 Booster Spirituel", "key": "boosts", "target": 1},
    {"name": "🧵 Petit créateur", "key": "threads", "target": 5},
    {"name": "🧶 Tisseur d’infos", "key": "threads", "target": 15},
    {"name": "🧵🧵🧵 Architecte des fils", "key": "threads", "target": 50},
    {"name": "🎤 Début de voix", "key": "vocal_minutes", "target": 60},
    {"name": "🎧 Marathon vocal", "key": "vocal_minutes", "target": 600},
    {"name": "🌀 Dieu du vocal", "key": "vocal_minutes", "target": 6000},
    {"name": "📩 Messager", "key": "messages", "target": 50},
    {"name": "📬 Communicant", "key": "messages", "target": 400},
    {"name": "📝 Scribe du néant", "key": "messages", "target": 1000},
]

class ProgressionAnnouncer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        user = message.author
        guild = message.guild
        user_id = str(user.id)
        guild_id = str(guild.id)

        user_data = await user_collection.find_one({"user_id": user_id, "guild_id": guild_id})
        if not user_data:
            user_data = {
                "user_id": user_id,
                "guild_id": guild_id,
                "xp": XP_PER_MESSAGE,
                "level": 1,
                "messages": 1,
                "vocal_minutes": 0
            }
            await user_collection.insert_one(user_data)
        else:
            await user_collection.update_one(
                {"user_id": user_id, "guild_id": guild_id},
                {"$inc": {"xp": XP_PER_MESSAGE, "messages": 1}}
            )
            user_data["xp"] += XP_PER_MESSAGE
            user_data["messages"] += 1

        # === NIVEAU ===
        xp = user_data["xp"]
        level = user_data["level"]
        next_level_xp = 100 + (level * 100)

        if xp >= next_level_xp:
            new_level = level + 1
            await user_collection.update_one(
                {"user_id": user_id, "guild_id": guild_id},
                {"$set": {"level": new_level}}
            )

            # Rôles
            role_to_add = None
            roles_to_remove = []
            for lvl, role_id in LEVEL_ROLES.items():
                role = guild.get_role(role_id)
                if new_level >= lvl:
                    role_to_add = role
                if role in user.roles and new_level < lvl:
                    roles_to_remove.append(role)

            if role_to_add and role_to_add not in user.roles:
                await user.add_roles(role_to_add)
                for r in roles_to_remove:
                    await user.remove_roles(r)

            # Annonce montée de niveau
            channel = guild.get_channel(ANNOUNCE_CHANNEL_ID)
            if channel:
                card = await generate_rank_card(
                    member=user,
                    level=new_level,
                    xp=xp,
                    next_level_xp=100 + (new_level * 100),
                    total_messages=user_data["messages"],
                    total_vocal=user_data.get("vocal_minutes", 0)
                )
                file = discord.File(card, filename="rank.png")
                await channel.send(
                    content=f"🌟 {user.mention} vient de passer **niveau {new_level}** avec {xp} XP !",
                    file=file
                )

        # === SUCCÈS ===
        for success in SUCCESS_LIST:
            key = success["key"]
            target = success["target"]
            val = user_data.get(key, 0)

            # messages vient d’être mis à jour ici
            if key == "messages":
                val += 1

            # Vérifie si succès non déjà validé
            already_complete = user_data.get(f"{key}_success_{target}", False)
            if val >= target and not already_complete:
                await user_collection.update_one(
                    {"user_id": user_id, "guild_id": guild_id},
                    {"$set": {f"{key}_success_{target}": True}}
                )

                # Envoi message succès
                channel = guild.get_channel(ANNOUNCE_CHANNEL_ID)
                if channel:
                    card = await generate_rank_card(
                        member=user,
                        level=user_data.get("level", 1),
                        xp=user_data["xp"],
                        next_level_xp=next_level_xp,
                        total_messages=user_data["messages"],
                        total_vocal=user_data.get("vocal_minutes", 0)
                    )
                    file = discord.File(card, filename="rank.png")
                    await channel.send(
                        content=f"🏅 {user.mention} a débloqué le succès **{success['name']}** !",
                        file=file
                    )

async def setup(bot: commands.Bot):
    await bot.add_cog(ProgressionAnnouncer(bot))
