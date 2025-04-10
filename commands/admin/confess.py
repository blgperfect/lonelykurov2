import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Modal, TextInput, button
from datetime import datetime
import locale

# === CONFIGURATION FIXE ===
CONFESSION_CHANNEL_ID = 1357122783683018846
MENTION_ROLE_ID = 1348573569440940052
EMBED_COLOR = discord.Color.from_str("#C49DFF")

MAX_CONFESSION_LENGTH = 1000
MAX_REPLY_LENGTH = 1000

# 🇫🇷 Mettre la locale pour format en français (si dispo sur ton OS)
try:
    locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
except:
    locale.setlocale(locale.LC_TIME, "")  # fallback

# ---------- MODAL CONFESSION ----------
class ConfessModal(Modal):
    def __init__(self, bot):
        super().__init__(title="Confession anonyme")
        self.bot = bot
        self.text = TextInput(
            label="Ta confession",
            style=discord.TextStyle.paragraph,
            max_length=MAX_CONFESSION_LENGTH
        )
        self.add_item(self.text)

    async def on_submit(self, interaction: discord.Interaction):
        channel = self.bot.get_channel(CONFESSION_CHANNEL_ID)
        if not channel:
            return await interaction.response.send_message("❌ Salon de confession introuvable.", ephemeral=True)

        heure_locale = datetime.now().strftime("%d %B %Y à %H:%M")
        role_mention = f"<@&{MENTION_ROLE_ID}>"

        embed = discord.Embed(
            title="🌫️ Nouvelle confession anonyme",
            description=self.text.value,
            color=EMBED_COLOR
        )
        embed.set_footer(text=f"Envoyée anonymement • {heure_locale}")

        sent_message = await channel.send(content=role_mention, embed=embed)
        await sent_message.edit(view=ConfessButtonView(self.bot, sent_message))

        await interaction.response.send_message("✅ Confession envoyée anonymement.", ephemeral=True)

# ---------- MODAL RÉPONSE ----------
class ConfessReplyModal(Modal):
    def __init__(self, bot, original_message):
        super().__init__(title="Répondre anonymement")
        self.bot = bot
        self.original_message = original_message
        self.input = TextInput(
            label="Ta réponse anonyme",
            style=discord.TextStyle.paragraph,
            max_length=MAX_REPLY_LENGTH
        )
        self.add_item(self.input)

    async def on_submit(self, interaction: discord.Interaction):
        heure_locale = datetime.now().strftime("%d %B %Y à %H:%M")

        embed = discord.Embed(
            title="💬 Réponse à la confession",
            description=self.input.value,
            color=EMBED_COLOR
        )
        embed.set_footer(text=f"Réponse anonyme • {heure_locale}")

        try:
            await self.original_message.reply(embed=embed)
            await interaction.response.send_message("✅ Réponse envoyée anonymement.", ephemeral=True)
        except:
            await interaction.response.send_message("❌ Erreur lors de l'envoi de la réponse.", ephemeral=True)

# ---------- VUE POUR RÉPONDRE ----------
class ConfessButtonView(View):
    def __init__(self, bot, original_message):
        super().__init__(timeout=None)
        self.bot = bot
        self.original_message = original_message

    @button(label="Répondre anonymement", style=discord.ButtonStyle.secondary)
    async def respond(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ConfessReplyModal(self.bot, self.original_message))

# ---------- COG PRINCIPAL ----------
class ConfessCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="confess", description="Envoyer une confession anonyme")
    async def confess(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ConfessModal(self.bot))

# ---------- SETUP ----------
async def setup(bot: commands.Bot):
    await bot.add_cog(ConfessCog(bot))
