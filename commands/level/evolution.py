import discord
from discord import app_commands
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

COLOR = discord.Color.from_str("#C9B6D9")

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
    {"name": "👑 Légende vivante", "key": "mastery", "target": 1},
]

class Evolution(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="evolution", description="Voir la progression de tes succès.")
    async def evolution(self, interaction: discord.Interaction):
        await interaction.response.defer()

        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild.id)

        user_data = await user_collection.find_one({"user_id": user_id, "guild_id": guild_id})

        if not user_data:
            await interaction.followup.send("Tu n’as pas encore débloqué de succès.")
            return

        embed = discord.Embed(
            title=f"✨ Succès de {interaction.user.display_name}",
            description="Voici l'avancée de ta quête personnelle !",
            color=COLOR
        )

        completed = 0
        for s in SUCCESS_LIST:
            current = user_data.get(s["key"], 0)
            target = s["target"]
            check = "✅" if current >= target else "❌"
            progress = f"{min(current, target)}/{target}"
            embed.add_field(name=f"{check} {s['name']}", value=progress, inline=False)
            if current >= target:
                completed += 1

        # Débloque "Légende vivante" automatiquement
        if completed >= 12:
            await user_collection.update_one(
                {"user_id": user_id, "guild_id": guild_id},
                {"$set": {"mastery": 1}}
            )

        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Evolution(bot))
