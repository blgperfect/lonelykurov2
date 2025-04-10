import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

class UserInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="user-info", description="Affiche les informations d'un utilisateur, y compris sa bannière.")
    @app_commands.describe(
        membre="Le membre dont vous souhaitez voir les informations."
    )
    async def user_info(self, interaction: discord.Interaction, membre: discord.Member):
        # On récupère la liste des rôles (hors @everyone)
        roles = [r.mention for r in membre.roles if r != interaction.guild.default_role]
        roles_str = ", ".join(roles) if roles else "Aucun"

        # Infos de base
        pseudo = membre.name
        user_id = membre.id
        nickname = membre.nick if membre.nick else "Aucun"
        avatar_url = membre.display_avatar.url
        date_creation = membre.created_at.strftime("%A, %B %d %Y %H:%M")
        date_arrivee = (
            membre.joined_at.strftime("%A, %B %d %Y %H:%M")
            if membre.joined_at
            else "Inconnue"
        )

        # Récupération du user complet pour la bannière
        user_fetched = await self.bot.fetch_user(membre.id)
        banner_url = user_fetched.banner.url if user_fetched.banner else None

        # Badges
        badges = []
        if user_fetched.public_flags.active_developer:
            badges.append("ActiveDeveloper")
        # Ajoutez d'autres flags si besoin
        badges_str = ", ".join(badges) if badges else "Aucun"

        # Construction de l'embed
        embed = discord.Embed(
            title=f"Information sur {pseudo}",
            color=0xcbb5f1,
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=avatar_url)
        embed.add_field(name="Pseudo :", value=pseudo, inline=True)
        embed.add_field(name="ID :", value=str(user_id), inline=True)
        embed.add_field(name="Avatar :", value=f"[Lien]({avatar_url})", inline=False)
        embed.add_field(name="Badges :", value=badges_str, inline=False)
        embed.add_field(name="Date de création du compte :", value=date_creation, inline=False)
        embed.add_field(
            name="Information sur le membre",
            value=(
                f"**Surnom :** {nickname}\n"
                f"**Rôles :** {roles_str}\n"
                f"**Date d'arrivée :** {date_arrivee}"
            ),
            inline=False
        )

        # Si l'utilisateur possède une bannière, on l'affiche en bas
        if banner_url:
            embed.set_image(url=banner_url)

        embed.set_footer(
            text=f"Demandé par {interaction.user}",
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.response.send_message(embed=embed, ephemeral=False)

async def setup(bot):
    await bot.add_cog(UserInfo(bot))