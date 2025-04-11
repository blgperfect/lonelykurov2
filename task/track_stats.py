import discord
from discord.ext import tasks, commands
import motor.motor_asyncio
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]
stats_collection = db["server_stats"]

class StatsTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_counts = {}  # {guild_id: {user_id: count}}
        self.vocal_times = {}     # {guild_id: {user_id: timedelta}}
        self.active_vocals = {}   # {guild_id: {user_id: join_time}}
        self.track_stats.start()

    def cog_unload(self):
        self.track_stats.cancel()

    # === MESSAGES TRACKING ===
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        gid = message.guild.id
        uid = message.author.id
        self.message_counts.setdefault(gid, {}).setdefault(uid, 0)
        self.message_counts[gid][uid] += 1

    # === VOCAL TIME TRACKING ===
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        gid = member.guild.id
        uid = member.id

        self.active_vocals.setdefault(gid, {})
        self.vocal_times.setdefault(gid, {})
        now = datetime.utcnow()

        if before.channel is None and after.channel is not None:
            self.active_vocals[gid][uid] = now
        elif before.channel is not None and after.channel is None:
            join_time = self.active_vocals[gid].pop(uid, None)
            if join_time:
                duration = now - join_time
                self.vocal_times[gid][uid] = self.vocal_times[gid].get(uid, timedelta()) + duration

    # === DAILY STATS FLUSH ===
    @tasks.loop(hours=24)
    async def track_stats(self):
        print("[STATS] Compilation quotidienne en cours...")
        for guild_id, users in self.message_counts.items():
            for user_id, count in users.items():
                await self._update_user_stats(guild_id, user_id, messages=count)

        for guild_id, users in self.vocal_times.items():
            for user_id, duration in users.items():
                hours = round(duration.total_seconds() / 3600, 2)
                await self._update_user_stats(guild_id, user_id, vocal_time=hours)

        self.message_counts.clear()
        self.vocal_times.clear()

    @track_stats.before_loop
    async def before_track(self):
        await self.bot.wait_until_ready()

    # === MONGO UPDATE ===
    async def _update_user_stats(self, guild_id, user_id, messages=0, vocal_time=0.0):
        key = {"_id": user_id}
        user_data = await stats_collection.find_one(key) or {"_id": user_id, "guild_id": guild_id}

        # Update rolling stats
        messages_history = user_data.get("messages", {}).get("history", [])
        vocal_history = user_data.get("vocal_time", {}).get("history", [])

        messages_history = (messages_history + [messages])[-14:]
        vocal_history = (vocal_history + [vocal_time])[-14:]

        # Rebuild the fields
        user_data["messages"] = {
            "1j": messages,
            "7j": sum(messages_history[-7:]),
            "14j": sum(messages_history),
            "history": messages_history
        }
        user_data["vocal_time"] = {
            "1j": vocal_time,
            "7j": round(sum(vocal_history[-7:]), 2),
            "14j": round(sum(vocal_history), 2),
            "history": vocal_history
        }

        await stats_collection.update_one(key, {"$set": user_data}, upsert=True)

# === EXTENSION ===
async def setup(bot):
    await bot.add_cog(StatsTracker(bot))
