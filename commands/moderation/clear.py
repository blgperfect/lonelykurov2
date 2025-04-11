from discord.ext import commands
from discord import app_commands
import discord

class ClearCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    # Slash command: /clear amount:<int>
    @app_commands.command(name="clear", description="Supprime des messages dans ce salon")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.describe(amount="Nombre de messages à supprimer (max 100)")
    async def clear_slash(self, interaction: discord.Interaction, amount: int):
        if amount < 1 or amount > 100:
            return await interaction.response.send_message("❌ Entre un nombre entre 1 et 100.", ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount, check=lambda m: not m.pinned)
        await interaction.response.send_message(f"✅ {len(deleted)} messages supprimés.", ephemeral=True)

    # Gestion erreur : manque de permissions


    @clear_slash.error
    async def clear_slash_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ Tu n’as pas la permission `Gérer les messages`.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ClearCommand(bot))
