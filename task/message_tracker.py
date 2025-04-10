import discord
from discord.ext import commands
import motor.motor_asyncio
from dotenv import load_dotenv
import os

# === Chargement MongoDB ===
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DATABASE_NAME]
user_collection = db["users"]

XP_PER_MESSAGE = 10  # Tu peux modifier ici

class MessageTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        user_id = str(message.author.id)
        guild_id = str(message.guild.id)

        user_data = await user_collection.find_one({"user_id": user_id, "guild_id": guild_id})

        if not user_data:
            await user_collection.insert_one({
                "user_id": user_id,
                "guild_id": guild_id,
                "xp": XP_PER_MESSAGE,
                "level": 1,
                "messages": 1,
                "vocal_minutes": 0
            })
        else:
            await user_collection.update_one(
                {"user_id": user_id, "guild_id": guild_id},
                {
                    "$inc": {
                        "messages": 1,
                        "xp": XP_PER_MESSAGE
                    }
                }
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(MessageTracker(bot))
