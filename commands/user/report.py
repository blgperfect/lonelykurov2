import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import os
import motor.motor_asyncio
from dotenv import load_dotenv

# === CONFIGURATION ===
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client["kurozen_system"]
reports_col = db["user_reports"]

REPORT_CHANNEL_ID = 1359654610767446186
EMBED_COLOR = discord.Color.from_str("#B283E6")

class Report(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="report", description="Signaler un utilisateur au staff.")
    @app_commands.describe(
        user="Utilisateur à signaler",
        raison="Explique ce qui s'est passé (obligatoire)",
        preuve="Capture d'écran ou fichier (facultatif)"
    )
    async def report(self, interaction: discord.Interaction, user: discord.User, raison: str, preuve: discord.Attachment = None):
        await interaction.response.send_message("📨 Ton signalement a été envoyé au staff. Merci !", ephemeral=True)

        # === Incrémenter compteur de reports pour l'utilisateur ciblé
        doc = await reports_col.find_one({"user_id": user.id})
        report_count = (doc["count"] + 1) if doc else 1
        if doc:
            await reports_col.update_one({"user_id": user.id}, {"$set": {"count": report_count}})
        else:
            await reports_col.insert_one({"user_id": user.id, "count": 1})

        # === Envoi dans le salon de modération
        channel = interaction.guild.get_channel(REPORT_CHANNEL_ID)
        if not channel:
            return

        embed = discord.Embed(
            title="🚨 Nouveau Report Utilisateur",
            color=EMBED_COLOR,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="👤 Utilisateur signalé", value=f"{user.mention} (`{user.id}`)", inline=False)
        embed.add_field(name="📨 Signalé par", value=f"{interaction.user.mention} (`{interaction.user.id}`)", inline=False)
        embed.add_field(name="📝 Raison", value=raison, inline=False)
        embed.add_field(name="📊 Nombre de signalements", value=f"{report_count} report(s)", inline=False)

        if preuve:
            embed.set_image(url=preuve.url)

        embed.set_footer(text="Système de report automatique")
        await channel.send(embed=embed)

# === EXTENSION ===
async def setup(bot):
    await bot.add_cog(Report(bot))
