import discord
from discord.ext import commands
from discord import app_commands

class NicknameManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # === SLASH ===
    @app_commands.command(name="changenick", description="Changer le pseudo d'un membre.")
    @app_commands.describe(member="Membre à renommer", nickname="Nouveau pseudo (ou vide pour reset)")
    async def changenick_slash(self, interaction: discord.Interaction, member: discord.Member, nickname: str = None):
        if not interaction.user.guild_permissions.manage_nicknames:
            return await interaction.response.send_message("❌ Tu n’as pas la permission `Gérer les pseudos`.", ephemeral=True)

        if member.top_role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
            return await interaction.response.send_message("❌ Ce membre est trop haut dans la hiérarchie.", ephemeral=True)

        if member.top_role >= interaction.guild.me.top_role:
            return await interaction.response.send_message("❌ Je ne peux pas modifier ce membre (rôle trop haut).", ephemeral=True)

        try:
            await member.edit(nick=nickname, reason=f"Changé par {interaction.user}")
            msg = f"✅ Pseudo de {member.mention} mis à jour."
            msg += f" Nouveau pseudo : **{nickname}**" if nickname else " Pseudo réinitialisé."
            await interaction.response.send_message(msg)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Je n'ai pas la permission de changer ce pseudo.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ Erreur : `{type(e).__name__}` - {e}", ephemeral=True)

    # === PREFIX ===
    @commands.command(name="changenick")
    @commands.has_permissions(manage_nicknames=True)
    async def changenick_prefix(self, ctx, member: discord.Member, *, nickname: str = None):
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send("❌ Tu ne peux pas changer le pseudo de ce membre (hiérarchie).")

        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.send("❌ Je ne peux pas changer le pseudo de ce membre (rôle trop haut pour moi).")

        try:
            await member.edit(nick=nickname, reason=f"Changé par {ctx.author}")
            msg = f"✅ Pseudo de {member.mention} mis à jour."
            msg += f" Nouveau pseudo : **{nickname}**" if nickname else " Pseudo réinitialisé."
            await ctx.send(msg)
        except discord.Forbidden:
            await ctx.send("❌ Je n’ai pas la permission de changer ce pseudo.")
        except Exception as e:
            await ctx.send(f"⚠️ Erreur : `{type(e).__name__}` - {e}")

async def setup(bot):
    await bot.add_cog(NicknameManager(bot))
