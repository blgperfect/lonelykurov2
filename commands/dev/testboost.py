# commands/dev/testboost.py
# non obligatoire juste pour tester ! you dont have to keep this is just for testing
import discord
from discord.ext import commands
from discord import app_commands

DEV_ID = 808313178739048489  # Toi uniquement

class TestBoostCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="testboost")
    async def testboost_prefix(self, ctx: commands.Context):
        if ctx.author.id != DEV_ID:
            await ctx.send("🚫 Cette commande est réservée au développeur.", delete_after=5)
            return
        await ctx.send("📡 Simulation de boost (prefix)", delete_after=5)
        await self.simulate_boost(ctx.author)

    @app_commands.command(name="testboost", description="Tester l'envoi du message de boost automatique")
    async def testboost_slash(self, interaction: discord.Interaction):
        if interaction.user.id != DEV_ID:
            await interaction.response.send_message("🚫 Cette commande est réservée au développeur.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("📡 Simulation de boost (slash)", ephemeral=True)
        await self.simulate_boost(interaction.user)

    async def simulate_boost(self, member: discord.Member):
        task = self.bot.get_cog("BoostAutoTask")
        if task is None:
            print("❌ BoostAutoTask non chargé.")
            return
        await task.send_boost_message(member)

async def setup(bot):
    await bot.add_cog(TestBoostCommand(bot))
    print("✅ TestBoostCommand bien enregistré.")
