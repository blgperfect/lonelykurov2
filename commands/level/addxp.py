import discord
from discord import app_commands
from discord.ext import commands
import motor.motor_asyncio
from dotenv import load_dotenv
import os

# === Connexion MongoDB ===
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DATABASE_NAME]
user_collection = db["users"]

COLOR = discord.Color.from_str("#C9B6D9")

class AddXP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addxp", description="Ajoute de l’XP à un utilisateur.")
    @app_commands.describe(member="Membre à qui donner de l’XP", amount="Montant d’XP à ajouter")
    @app_commands.checks.has_permissions(administrator=True)
    async def addxp(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        await interaction.response.defer()

        user_id = str(member.id)
        guild_id = str(interaction.guild.id)

        user_data = await user_collection.find_one({"user_id": user_id, "guild_id": guild_id})
        if not user_data:
            await user_collection.insert_one({
                "user_id": user_id,
                "guild_id": guild_id,
                "xp": amount,
                "level": 1,
                "messages": 0,
                "vocal_minutes": 0
            })
        else:
            await user_collection.update_one(
                {"user_id": user_id, "guild_id": guild_id},
                {"$inc": {"xp": amount}}
            )

        embed = discord.Embed(
            title="✨ XP Ajoutée",
            description=f"💠 {amount} XP ajoutés à {member.mention}.",
            color=COLOR
        )
        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(AddXP(bot))
