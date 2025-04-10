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

# === Style Embed ===
COLOR = discord.Color.from_str("#C9B6D9")

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="leaderboard", description="Voir le classement des meilleurs XP du serveur.")
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer()

        guild_id = str(interaction.guild.id)
        users = await user_collection.find({"guild_id": guild_id}).sort("xp", -1).to_list(length=10)

        if not users:
            await interaction.followup.send("Aucun utilisateur n'a encore gagné d'XP.")
            return

        embed = discord.Embed(
            title="🏆 Classement XP du Serveur",
            description="Les membres les plus actifs sont ici !",
            color=COLOR
        )

        for index, user in enumerate(users, start=1):
            member = interaction.guild.get_member(int(user["user_id"]))
            if not member:
                continue
            name = member.display_name
            xp = user.get("xp", 0)
            level = user.get("level", 1)
            embed.add_field(
                name=f"#{index} - {name}",
                value=f"🔮 Niveau **{level}** — 💜 **{xp} XP**",
                inline=False
            )

        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Leaderboard(bot))
