# confess.py
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Modal, TextInput, button
from datetime import datetime
import locale

# === CONFIGURATION ===
CONFESSION_CHANNEL_ID = 1357122783683018846
MENTION_ROLE_ID = 1348573569440940052
EMBED_COLOR = discord.Color.from_str("#C49DFF")

MAX_CONFESSION_LENGTH = 1000
MAX_REPLY_LENGTH = 1000

try:
    locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
except:
    locale.setlocale(locale.LC_TIME, "")

# --- MODAL DE CONFESSION ---
class ConfessModal(Modal):
    def __init__(self, bot):
        super().__init__(title="Confession anonyme")
        self.bot = bot
        self.text = TextInput(label="Ta confession", style=discord.TextStyle.paragraph, max_length=MAX_CONFESSION_LENGTH)
        self.add_item(self.text)

    async def on_submit(self, interaction: discord.Interaction):
        channel = self.bot.get_channel(CONFESSION_CHANNEL_ID)
        if not channel:
            return await interaction.response.send_message("❌ Salon introuvable.", ephemeral=True)

        heure = datetime.now().strftime("%d %B %Y à %H:%M")
        role_ping = f"<@&{MENTION_ROLE_ID}>"

        embed = discord.Embed(title="🌫️ Nouvelle confession anonyme", description=self.text.value, color=EMBED_COLOR)
        embed.set_footer(text=f"Envoyée anonymement • {heure}")

        sent = await channel.send(content=role_ping, embed=embed, view=ConfessButtonView(self.bot))
        await interaction.response.send_message("✅ Confession envoyée.", ephemeral=True)

# --- MODAL DE RÉPONSE ---
class ConfessReplyModal(Modal):
    def __init__(self, bot, original_message: discord.Message):
        super().__init__(title="Répondre anonymement")
        self.bot = bot
        self.original_message = original_message
        self.input = TextInput(label="Ta réponse anonyme", style=discord.TextStyle.paragraph, max_length=MAX_REPLY_LENGTH)
        self.add_item(self.input)

    async def on_submit(self, interaction: discord.Interaction):
        heure = datetime.now().strftime("%d %B %Y à %H:%M")
        embed = discord.Embed(title="💬 Réponse à la confession", description=self.input.value, color=EMBED_COLOR)
        embed.set_footer(text=f"Réponse anonyme • {heure}")

        try:
            await self.original_message.reply(embed=embed)
            await interaction.response.send_message("✅ Réponse envoyée.", ephemeral=True)
        except:
            await interaction.response.send_message("❌ Erreur lors de l'envoi de la réponse.", ephemeral=True)

# --- VUE AVEC BOUTON ---
class ConfessButtonView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @button(label="Répondre anonymement", style=discord.ButtonStyle.secondary, custom_id="confess_reply")
    async def respond(self, interaction: discord.Interaction, button: discord.ui.Button):
        message = interaction.message  # Récupération dynamique
        await interaction.response.send_modal(ConfessReplyModal(self.bot, message))

# --- COG PRINCIPAL ---
class ConfessCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="confess", description="Envoyer une confession anonyme")
    async def confess(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ConfessModal(self.bot))

# --- SETUP DU COG ---
async def setup(bot: commands.Bot):
    await bot.add_cog(ConfessCog(bot))
    bot.add_view(ConfessButtonView(bot))  # Nécessaire pour que les boutons fonctionnent après redémarrage
