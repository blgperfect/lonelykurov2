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

    ### ----- PREFIX: ADD ROLE ----- ###
    @commands.command(name="addrole")
    @commands.has_permissions(manage_roles=True)
    async def addrole_cmd(self, ctx, member: discord.Member, role: discord.Role):
        if not self.can_manage_role(ctx.author, member, role):
            return await ctx.send("❌ Tu ne peux pas ajouter ce rôle. Trop haut ou membre protégé.")
        try:
            if role in member.roles:
                return await ctx.send("⚠️ Ce membre a déjà ce rôle.")
            await member.add_roles(role)
            await ctx.send(f"✅ Rôle **{role.name}** ajouté à {member.mention}.")
        except Exception as e:
            await ctx.send(f"🚫 Erreur lors de l'ajout du rôle : `{type(e).__name__}` - {e}")

    ### ----- PREFIX: REMOVE ROLE ----- ###
    @commands.command(name="removerole")
    @commands.has_permissions(manage_roles=True)
    async def removerole_cmd(self, ctx, member: discord.Member, role: discord.Role):
        if not self.can_manage_role(ctx.author, member, role):
            return await ctx.send("❌ Tu ne peux pas retirer ce rôle. Trop haut ou membre protégé.")
        try:
            if role not in member.roles:
                return await ctx.send("⚠️ Ce membre n’a pas ce rôle.")
            await member.remove_roles(role)
            await ctx.send(f"✅ Rôle **{role.name}** retiré de {member.mention}.")
        except Exception as e:
            await ctx.send(f"🚫 Erreur lors du retrait du rôle : `{type(e).__name__}` - {e}")

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
