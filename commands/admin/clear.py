from discord.ext import commands
from discord import app_commands
import discord

class ClearCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Prefix command: !clear <amount>
    @commands.command(name="clear")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        if amount < 1 or amount > 100:
            return await ctx.send("❌ Choisis un nombre entre 1 et 100.", delete_after=5)
        deleted = await ctx.channel.purge(limit=amount + 1, check=lambda m: not m.pinned)
        await ctx.send(f"✅ {len(deleted) - 1} messages supprimés.", delete_after=3)

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
    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Permission `Gérer les messages` requise.", delete_after=5)

    @clear_slash.error
    async def clear_slash_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ Tu n’as pas la permission `Gérer les messages`.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ClearCommand(bot))
