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
    {"key": "reactions", "target": 50, "points": 5},
    {"key": "reactions", "target": 800, "points": 10},
    {"key": "boosts", "target": 1, "points": 15},
    {"key": "threads", "target": 5, "points": 5},
    {"key": "threads", "target": 15, "points": 10},
    {"key": "threads", "target": 50, "points": 15},
    {"key": "vocal_minutes", "target": 60, "points": 5},
    {"key": "vocal_minutes", "target": 600, "points": 10},
    {"key": "vocal_minutes", "target": 6000, "points": 20},
    {"key": "messages", "target": 50, "points": 5},
    {"key": "messages", "target": 400, "points": 10},
    {"key": "messages", "target": 1000, "points": 20},
    {"key": "mastery", "target": 1, "points": 30},
]

class EvolutionStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def calculate_points(self, data):
        score = 0
        for s in SUCCESS_LIST:
            if data.get(s["key"], 0) >= s["target"]:
                score += s["points"]
        return score

    @app_commands.command(name="evolution_stats", description="Classement des membres selon leurs succès.")
    async def evolution_stats(self, interaction: discord.Interaction):
        await interaction.response.defer()

        guild_id = str(interaction.guild.id)
        all_users = await user_collection.find({"guild_id": guild_id}).to_list(length=None)

        ranked = sorted(all_users, key=self.calculate_points, reverse=True)[:10]

        embed = discord.Embed(
            title="📊 Classement des Succès",
            description="Voici les membres les plus accomplis !",
            color=COLOR
        )

        for i, user in enumerate(ranked, start=1):
            member = interaction.guild.get_member(int(user["user_id"]))
            if not member:
                continue
            points = self.calculate_points(user)
            embed.add_field(name=f"#{i} - {member.display_name}", value=f"🌟 {points} points de succès", inline=False)

        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(EvolutionStats(bot))
