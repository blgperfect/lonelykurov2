import discord
from discord.ext import commands
from datetime import datetime
import asyncio

# === CONFIGURATION ===
MESSAGE_LOG_CHANNEL_ID = 1359649981555802223
EMBED_COLOR_EDIT = discord.Color.from_str("#faa61a")   # Orange Carl-bot style
EMBED_COLOR_DELETE = discord.Color.from_str("#e74c3c") # Rouge Carl-bot style

class MessageLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # === MESSAGE SUPPRIMÉ
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        channel = message.guild.get_channel(MESSAGE_LOG_CHANNEL_ID)
        if not channel:
            return

        # Try to detect who deleted it (audit logs)
        deleter = None
        try:
            await asyncio.sleep(1)
            async for entry in message.guild.audit_logs(limit=6, action=discord.AuditLogAction.message_delete):
                if entry.target.id == message.author.id and abs((discord.utils.utcnow() - entry.created_at).total_seconds()) < 5:
                    deleter = entry.user
                    break
        except Exception:
            pass

        embed = discord.Embed(
            title=f"🗑️ Message supprimé dans {message.channel.mention}",
            description=message.content if message.content else "*Aucun contenu texte.*",
            color=EMBED_COLOR_DELETE,
            timestamp=datetime.utcnow()
        )
        embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
        embed.add_field(name="Message ID", value=message.id, inline=False)
        if deleter and deleter.id != message.author.id:
            embed.add_field(name="Supprimé par", value=f"{deleter.mention}", inline=False)

        embed.set_footer(text=f"ID: {message.id} | {datetime.utcnow().strftime('Aujourd’hui à %H:%M')}")
        await channel.send(embed=embed)

    # === MESSAGE MODIFIÉ
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot or not before.guild or before.content == after.content:
            return

        channel = before.guild.get_channel(MESSAGE_LOG_CHANNEL_ID)
        if not channel:
            return

        embed = discord.Embed(
            title=f"✏️ Message modifié dans {before.channel.mention}",
            color=EMBED_COLOR_EDIT,
            timestamp=datetime.utcnow()
        )
        embed.set_author(name=str(before.author), icon_url=before.author.display_avatar.url)
        embed.add_field(name="Avant :", value=before.content[:1024] or "*vide*", inline=False)
        embed.add_field(name="Après :", value=after.content[:1024] or "*vide*", inline=False)
        embed.add_field(name="Message ID", value=before.id, inline=False)
        embed.set_footer(text=f"ID: {before.id} | {datetime.utcnow().strftime('Aujourd’hui à %H:%M')}")
        await channel.send(embed=embed)

# === EXTENSION ===
async def setup(bot):
    await bot.add_cog(MessageLogger(bot))
