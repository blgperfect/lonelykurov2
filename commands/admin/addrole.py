import discord
from discord.ext import commands
from discord import app_commands

class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def can_manage_role(actor: discord.Member, target: discord.Member, role: discord.Role):
        return (
            role < actor.top_role and
            target.top_role < actor.top_role and
            role < actor.guild.me.top_role and
            actor != target
        )

    ### ----- SLASH: ADD ROLE ----- ###
    @app_commands.command(name="addrole", description="Ajoute un rôle à un membre.")
    @app_commands.describe(member="Membre cible", role="Rôle à donner")
    async def addrole_slash(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        if not interaction.user.guild_permissions.manage_roles:
            return await interaction.response.send_message("❌ Permission `Gérer les rôles` requise.", ephemeral=True)
        if not self.can_manage_role(interaction.user, member, role):
            return await interaction.response.send_message("❌ Rôle trop haut ou cible protégée.", ephemeral=True)
        try:
            if role in member.roles:
                return await interaction.response.send_message("⚠️ Ce membre a déjà ce rôle.", ephemeral=True)
            await member.add_roles(role)
            await interaction.response.send_message(f"✅ Rôle **{role.name}** ajouté à {member.mention}.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"🚫 Erreur : `{type(e).__name__}` - {e}", ephemeral=True)

    ### ----- SLASH: REMOVE ROLE ----- ###
    @app_commands.command(name="removerole", description="Retire un rôle à un membre.")
    @app_commands.describe(member="Membre cible", role="Rôle à retirer")
    async def removerole_slash(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        if not interaction.user.guild_permissions.manage_roles:
            return await interaction.response.send_message("❌ Permission `Gérer les rôles` requise.", ephemeral=True)
        if not self.can_manage_role(interaction.user, member, role):
            return await interaction.response.send_message("❌ Rôle trop haut ou cible protégée.", ephemeral=True)
        try:
            if role not in member.roles:
                return await interaction.response.send_message("⚠️ Ce membre n’a pas ce rôle.", ephemeral=True)
            await member.remove_roles(role)
            await interaction.response.send_message(f"✅ Rôle **{role.name}** retiré de {member.mention}.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"🚫 Erreur : `{type(e).__name__}` - {e}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(RoleManager(bot))
