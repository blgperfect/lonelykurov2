import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="server-info", description="Affiche les informations complètes du serveur.")
    async def server_info(self, interaction: discord.Interaction):
        # Bannière → via fetch_guild
        full_guild = await self.bot.fetch_guild(interaction.guild.id)
        banner_url = full_guild.banner.url if full_guild.banner else None

        # Le reste via interaction.guild
        guild = interaction.guild
        owner = await self.bot.fetch_user(guild.owner_id)

        icon_url = guild.icon.url if guild.icon else None
        description = guild.description or "Aucune description"
        creation_date = guild.created_at.strftime("%A, %B %d %Y à %H:%M")

        # Membres
        total_members = guild.member_count
        humans = len([m for m in guild.members if not m.bot])
        bots = total_members - humans

        # Statistiques
        text_channels = len([c for c in guild.text_channels if not c.is_news()])
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        stage_channels = len([c for c in guild.stage_channels])
        forums = len([c for c in guild.channels if isinstance(c, discord.ForumChannel)])
        roles = len(guild.roles)
        emojis = guild.emojis

        # Salon de règles
        rules_channel = guild.rules_channel
        rules_value = rules_channel.mention if rules_channel else "Aucun"

        # Embed
        embed = discord.Embed(
            title=f"Informations sur le serveur\n{guild.name}",
            color=discord.Color.blurple(),
            timestamp=datetime.utcnow()
        )
        if icon_url:
            embed.set_thumbnail(url=icon_url)

        embed.add_field(name="📌 Informations sur le serveur", value=(
            f"**🆔 ID** : `{guild.id}`\n"
            f"**👑 Propriétaire** : {owner.mention}\n"
            f"**📝 Description** : {description}\n"
            f"**🚀 Boost** : {guild.premium_subscription_count} (Niveau {guild.premium_tier})\n"
            f"**🔞 NSFW** : {'Oui' if guild.nsfw_level.name != 'default' else 'Non'}\n"
            f"**👥 Membres** : {total_members} (👤 {humans} / 🤖 {bots})\n"
            f"**📆 Date de création** : {creation_date}"
        ), inline=False)

        embed.add_field(name="📊 Informations sur les statistiques", value=(
            f"**📁 Total des salons** : {len(guild.channels)}\n"
            f"**💬 Salons textuels** : {text_channels}\n"
            f"**🔊 Salons vocaux** : {voice_channels}\n"
            f"**🗂️ Catégories** : {categories}\n"
            f"**📰 Forums** : {forums}\n"
            f"**🎙️ Salons Stages** : {stage_channels}\n"
            f"**👑 Rôles** : {roles}\n"
            f"**😀 Emojis** : {len(emojis)}"
        ), inline=False)

        embed.add_field(name="📌 Informations sur les salons spéciaux", value=(
            f"**📜 Règlement** : {rules_value}"
        ), inline=False)

        # Preview emojis
        if emojis:
            emojis_preview = "".join(str(e) for e in emojis[:10])
            if len(emojis) > 10:
                emojis_preview += " ..."
            embed.add_field(name=f"😀 Emojis [{len(emojis)}]", value=emojis_preview, inline=False)

        # Affiche la bannière si dispo
        if banner_url:
            embed.set_image(url=banner_url)

        embed.set_footer(
            text=f"Demandé par {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.response.send_message(embed=embed, ephemeral=False)

async def setup(bot):
    await bot.add_cog(ServerInfo(bot))