import discord
from discord.ext import commands
import motor.motor_asyncio
from dotenv import load_dotenv
import os

# Chargement .env
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DATABASE_NAME]

# Collections utilisées
user_collection = db["users"]

class MemberExitCleanup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild_id = str(member.guild.id)
        user_id = str(member.id)

        await user_collection.delete_one({
            "user_id": user_id,
            "guild_id": guild_id
        })
        print(f"🗑️ Données supprimées pour {member} ({user_id}) dans le serveur {guild_id}")

async def setup(bot: commands.Bot):
    await bot.add_cog(MemberExitCleanup(bot))
