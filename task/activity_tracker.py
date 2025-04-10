import discord
from discord.ext import commands, tasks
import motor.motor_asyncio
from dotenv import load_dotenv
import os
import datetime

# Chargement des variables d'environnement
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DATABASE_NAME]
user_collection = db["users"]

# Dictionnaire pour stocker les heures d'entrée en vocal
voice_tracker = {}

class ActivityTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ========== VOCAL TRACKING ==========
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        user_id = str(member.id)
        guild_id = str(member.guild.id)

        if before.channel is None and after.channel is not None:
            # Entrée en vocal
            voice_tracker[user_id] = datetime.datetime.utcnow()
        elif before.channel is not None and after.channel is None:
            # Sortie du vocal
            if user_id in voice_tracker:
                join_time = voice_tracker.pop(user_id)
                now = datetime.datetime.utcnow()
                duration = int((now - join_time).total_seconds() // 60)  # en minutes

                await user_collection.update_one(
                    {"user_id": user_id, "guild_id": guild_id},
                    {"$inc": {"vocal_minutes": duration}},
                    upsert=True
                )

    # ========== RÉACTIONS ==========
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot or not reaction.message.guild:
            return

        user_id = str(user.id)
        guild_id = str(reaction.message.guild.id)

        await user_collection.update_one(
            {"user_id": user_id, "guild_id": guild_id},
            {"$inc": {"reactions": 1}},
            upsert=True
        )

    # ========== THREADS ==========
    @commands.Cog.listener()
    async def on_thread_create(self, thread):
        if not thread.guild or not thread.owner_id:
            return

        user_id = str(thread.owner_id)
        guild_id = str(thread.guild.id)

        await user_collection.update_one(
            {"user_id": user_id, "guild_id": guild_id},
            {"$inc": {"threads": 1}},
            upsert=True
        )

    # ========== BOOST ==========
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.premium_since is None and after.premium_since is not None:
            user_id = str(after.id)
            guild_id = str(after.guild.id)

            user_data = await user_collection.find_one({"user_id": user_id, "guild_id": guild_id})
            if not user_data or user_data.get("boosts", 0) == 0:
                await user_collection.update_one(
                    {"user_id": user_id, "guild_id": guild_id},
                    {"$set": {"boosts": 1}},
                    upsert=True
                )

async def setup(bot: commands.Bot):
    await bot.add_cog(ActivityTracker(bot))
