from discord.ext import commands
from discord import app_commands
import discord
import os
from dotenv import load_dotenv
import motor.motor_asyncio
from utils import stats_card

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]
stats_collection = db["server_stats"]

class StatsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="stats")
    async def stats(self, ctx):
        await ctx.message.delete()
        await self.send_user_stats(ctx.author, ctx)

    @app_commands.command(name="stats", description="Affiche tes statistiques personnelles (14j)")
    async def stats_slash(self, interaction: discord.Interaction):
        await self.send_user_stats(interaction.user, interaction)

    @commands.command(name="sserver")
    async def sserver(self, ctx):
        await ctx.message.delete()
        await self.send_server_stats(ctx.guild, ctx)

    @app_commands.command(name="sserver", description="Affiche les statistiques du serveur")
    async def sserver_slash(self, interaction: discord.Interaction):
        await self.send_server_stats(interaction.guild, interaction)

    async def send_user_stats(self, member, ctx_or_inter):
        try:
            data = await stats_collection.find_one({"_id": member.id})
            if not data:
                data = {
                    "_id": member.id,
                    "guild_id": member.guild.id if hasattr(member, "guild") else None,
                    "messages": {"1j": 0, "7j": 0, "14j": 0, "history": []},
                    "vocal_time": {"1j": 0.0, "7j": 0.0, "14j": 0.0, "history": []},
                    "top_text": "N/A",
                    "top_vocal": "N/A",
                    "graph_data": {
                        "messages": [0]*14,
                        "vocal": [0]*14
                    }
                }

            image_path = "assets/images/kuro1.png"
            await stats_card.generate_user_card(member, data, image_path)

            file = discord.File(image_path, filename="kuro1.png")
            embed = discord.Embed(
                title="📊 Tes statistiques (14 derniers jours)",
                color=discord.Color.purple()
            )
            embed.set_image(url="attachment://kuro1.png")

            if isinstance(ctx_or_inter, discord.Interaction):
                await ctx_or_inter.response.send_message(embed=embed, file=file)
            else:
                await ctx_or_inter.send(embed=embed, file=file)

        except Exception as e:
            msg = f"❌ Erreur dans `send_user_stats`: {type(e).__name__} - {e}"
            if isinstance(ctx_or_inter, discord.Interaction):
                await ctx_or_inter.response.send_message(msg, ephemeral=True)
            else:
                await ctx_or_inter.send(msg, delete_after=10)

    async def send_server_stats(self, guild, ctx_or_inter):
        try:
            data = await stats_collection.find_one({"_id": str(guild.id)})
            if not data:
                data = {
                    "_id": str(guild.id),
                    "messages": {"1j": 0, "7j": 0, "14j": 0},
                    "vocal_time": {"1j": 0.0, "7j": 0.0, "14j": 0.0},
                    "contributors": {"1j": 0, "7j": 0, "14j": 0},
                    "top_text": "N/A",
                    "top_vocal": "N/A",
                    "top_member_text": "N/A",
                    "top_member_vocal": "N/A",
                    "graph_data": {
                        "messages": [0]*14,
                        "vocal": [0]*14
                    }
                }

            image_path = "assets/images/kuro2.png"
            stats_card.generate_server_card(guild, data, image_path)  # NOT await

            file = discord.File(image_path, filename="kuro2.png")
            embed = discord.Embed(
                title="📈 Statistiques globales du serveur",
                color=discord.Color.purple()
            )
            embed.set_image(url="attachment://kuro2.png")

            if isinstance(ctx_or_inter, discord.Interaction):
                await ctx_or_inter.response.send_message(embed=embed, file=file)
            else:
                await ctx_or_inter.send(embed=embed, file=file)

        except Exception as e:
            msg = f"❌ Erreur dans `send_server_stats`: {type(e).__name__} - {e}"
            if isinstance(ctx_or_inter, discord.Interaction):
                await ctx_or_inter.response.send_message(msg, ephemeral=True)
            else:
                await ctx_or_inter.send(msg, delete_after=10)

    # === Gestion erreurs explicite ===
    @stats.error
    async def stats_error(self, ctx, error):
        await ctx.send(f"❌ Erreur `!stats`: {type(error).__name__} - {error}", delete_after=10)

    @stats_slash.error
    async def stats_slash_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message(f"❌ Erreur `/stats`: {type(error).__name__} - {error}", ephemeral=True)

    @sserver.error
    async def sserver_error(self, ctx, error):
        await ctx.send(f"❌ Erreur `!sserver`: {type(error).__name__} - {error}", delete_after=10)

    @sserver_slash.error
    async def sserver_slash_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message(f"❌ Erreur `/sserver`: {type(error).__name__} - {error}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(StatsCommand(bot))
