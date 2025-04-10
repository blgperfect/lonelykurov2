import os
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import motor.motor_asyncio
from datetime import datetime

# Helper pour créer des embeds standard avec la couleur par défaut #cbb5f1
def create_embed(title: str, description: str, color: int = 0xcbb5f1) -> discord.Embed:
    return discord.Embed(title=title, description=description, color=color)

# Charger les variables d'environnement
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
client_mongo = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)

db = client_mongo["kurozen_system"]  # 👈 ici tu forces la base que tu veux
suggestions_col = db["suggestions_config"]

# 🌸 MODAL de modération
class ModerationModal(discord.ui.Modal, title="Modération d'une suggestion"):
    numero = discord.ui.TextInput(label="Numéro de la suggestion", placeholder="Ex: 1", required=True)
    action = discord.ui.TextInput(label="Action (app / ref)", placeholder="app ou ref", required=True)
    raison = discord.ui.TextInput(label="Raison (facultative)", style=discord.TextStyle.paragraph, required=False)

    def __init__(self, bot, interaction):
        super().__init__()
        self.bot = bot
        self.interaction = interaction

    async def on_submit(self, interaction: discord.Interaction):
        num_str = self.numero.value.strip().lstrip('#')
        action_input = self.action.value.strip().lower()
        reason = self.raison.value.strip()

        try:
            suggestion_number = int(num_str)
        except ValueError:
            return await interaction.response.send_message(embed=create_embed("Erreur", "Le numéro doit être un entier."), ephemeral=True)

        if action_input.startswith("app"):
            action = "approuver"
        elif action_input.startswith("ref"):
            action = "refuser"
        else:
            return await interaction.response.send_message(embed=create_embed("Erreur", "L'action doit être 'app' ou 'ref'."), ephemeral=True)

        config = await suggestions_col.find_one({"guildId": str(interaction.guild.id)})
        if not config or "suggestions" not in config or "channelId" not in config["suggestions"]:
            return await interaction.response.send_message(embed=create_embed("Erreur", "Aucun salon de suggestions configuré."), ephemeral=True)

        messages_dict = config["suggestions"].get("messages", {})
        message_id_str = messages_dict.get(str(suggestion_number))
        if not message_id_str:
            return await interaction.response.send_message(embed=create_embed("Erreur", "Aucune suggestion trouvée pour ce numéro."), ephemeral=True)

        salon = interaction.guild.get_channel(int(config["suggestions"]["channelId"]))
        if not salon:
            return await interaction.response.send_message(embed=create_embed("Erreur", "Salon introuvable."), ephemeral=True)

        try:
            suggestion_message = await salon.fetch_message(int(message_id_str))
        except (discord.NotFound, discord.HTTPException):
            return await interaction.response.send_message(embed=create_embed("Erreur", "La suggestion n'a pas pu être récupérée."), ephemeral=True)

        embed_msg = suggestion_message.embeds[0]
        if any(field.name == "Modération" for field in embed_msg.fields):
            return await interaction.response.send_message(embed=create_embed("Erreur", "Cette suggestion a déjà été modérée."), ephemeral=True)

        mod_text = f"{action.capitalize()}"
        if reason:
            mod_text += f" - Raison : {reason}"
        mod_text += f"\nPar {interaction.user.display_name}"

        embed_msg.add_field(name="Modération", value=mod_text, inline=False)
        embed_msg.color = 0xb1f712 if action == "approuver" else 0xf44336

        try:
            await suggestion_message.edit(embed=embed_msg)
            succ = create_embed("Succès", f"Suggestion #{suggestion_number} {action}e avec succès.")
            await interaction.response.send_message(embed=succ, ephemeral=True)
        except discord.HTTPException:
            err = create_embed("Erreur", "Erreur lors de la mise à jour de la suggestion.")
            await interaction.response.send_message(embed=err, ephemeral=True)

# View interactive
class SuggestionsConfigView(discord.ui.View):
    def __init__(self, bot: commands.Bot, guild: discord.Guild):
        super().__init__(timeout=60)
        self.bot = bot
        self.guild = guild

    @discord.ui.button(label="Choisir le salon", style=discord.ButtonStyle.primary, custom_id="choisir_salon")
    async def choisir_salon(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = create_embed("Configuration", "Veuillez mentionner le salon pour les suggestions (ex: #général) :")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        try:
            msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == interaction.user and m.channel == interaction.channel,
                timeout=30
            )
        except asyncio.TimeoutError:
            err = create_embed("Erreur", "Temps écoulé, veuillez réessayer.")
            return await interaction.followup.send(embed=err, ephemeral=True)
        if not msg.channel_mentions:
            err = create_embed("Erreur", "Aucune mention détectée. Veuillez réessayer en mentionnant le salon.")
            return await interaction.followup.send(embed=err, ephemeral=True)
        salon = msg.channel_mentions[0]
        await suggestions_col.update_one(
            {"guildId": str(interaction.guild.id)},
            {"$set": {"suggestions.channelId": str(salon.id)}},
            upsert=True
        )
        try:
            await msg.delete()
        except Exception:
            pass
        succ = create_embed("Succès", f"Salon configuré : #{salon.name} pour les suggestions.")
        await interaction.followup.send(embed=succ, ephemeral=True)
    @discord.ui.button(label="Test suggestion", style=discord.ButtonStyle.secondary, custom_id="test_suggestion")
    async def test_suggestion(self, interaction: discord.Interaction, button: discord.ui.Button):
        config = await suggestions_col.find_one({"guildId": str(interaction.guild.id)})
        if not config or "suggestions" not in config or "channelId" not in config["suggestions"]:
            err = create_embed("Erreur", "Aucun salon sélectionné.")
            return await interaction.response.send_message(embed=err, ephemeral=True)
        salon = self.bot.get_channel(int(config["suggestions"]["channelId"]))
        if not salon:
            err = create_embed("Erreur", "Salon introuvable.")
            return await interaction.response.send_message(embed=err, ephemeral=True)
        fake_author = "Testeur"
        last_number = config.get("suggestions", {}).get("last_number", 0)
        suggestion_number = last_number + 1
        embed_msg = discord.Embed(
            title=f"Suggestion de {fake_author}",
            description="Ceci est une suggestion de test.",
            color=0xcbb5f1
        )
        embed_msg.set_footer(text=f"Suggestion #{suggestion_number}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
        embed_msg.timestamp = datetime.utcnow()
        msg = await salon.send(embed=embed_msg)
        for emoji in ["✅", "➖", "❌"]:
            await msg.add_reaction(emoji)
        new_values = {
            "suggestions.last_number": suggestion_number,
            f"suggestions.messages.{suggestion_number}": str(msg.id)
        }
        await suggestions_col.update_one(
            {"guildId": str(interaction.guild.id)},
            {"$set": new_values},
            upsert=True
        )
        succ = create_embed("Succès", f"Test suggestion envoyée dans #{salon.name} (Suggestion #{suggestion_number}).")
        await interaction.response.send_message(embed=succ, ephemeral=True)

    @discord.ui.button(label="Activer / Désactiver", style=discord.ButtonStyle.success, custom_id="toggle_system")
    async def toggle_system(self, interaction: discord.Interaction, button: discord.ui.Button):
        config = await suggestions_col.find_one({"guildId": str(interaction.guild.id)})
        current = config.get("suggestions", {}).get("enabled", False) if config else False
        new_status = not current
        await suggestions_col.update_one(
            {"guildId": str(interaction.guild.id)},
            {"$set": {"suggestions.enabled": new_status}},
            upsert=True
        )
        status = "activé" if new_status else "désactivé"
        succ = create_embed("Succès", f"Système {status}.")
        await interaction.response.send_message(embed=succ, ephemeral=True)

    @discord.ui.button(label="Gérer suggestions", style=discord.ButtonStyle.danger, custom_id="gerer_suggestions")
    async def gerer_suggestions(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ModerationModal(self.bot, interaction))

    @discord.ui.button(label="Réinitialiser suggestions", style=discord.ButtonStyle.danger, custom_id="reset_suggestions")
    async def reset_suggestions(self, interaction: discord.Interaction, button: discord.ui.Button):
        await suggestions_col.update_one(
            {"guildId": str(interaction.guild.id)},
            {"$set": {"suggestions.last_number": 0, "suggestions.messages": {}}},
            upsert=True
        )
        succ = create_embed("Succès", "Toutes les suggestions ont été réinitialisées.")
        await interaction.response.send_message(embed=succ, ephemeral=True)

# COG PRINCIPAL
class SuggestionsConfigCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="suggestions-config", description="Configure le système de suggestions.")
    async def suggestions_config(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Vous devez être administrateur pour utiliser cette commande.",
                ephemeral=True
            )
            return

        embed = create_embed("Configuration", "Utilise les boutons ci-dessous pour configurer ton système de suggestions.\n**Important : appuie sur Activé/Désactivé pour activer ou désactiver le système.**")
        await interaction.response.send_message(embed=embed, view=SuggestionsConfigView(self.bot, interaction.guild), ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        config = await suggestions_col.find_one({"guildId": str(message.guild.id)})
        if not config or not config.get("suggestions", {}).get("enabled", False):
            return
        salon_id = config.get("suggestions", {}).get("channelId")
        if not salon_id or message.channel.id != int(salon_id):
            return
        try:
            await message.delete()
        except discord.Forbidden:
            err = create_embed("Erreur", "Erreur lors de la suppression : vérifie mes permissions.")
            await message.channel.send(embed=err, delete_after=5)
            return
        last_number = config.get("suggestions", {}).get("last_number", 0)
        suggestion_number = last_number + 1
        embed_msg = discord.Embed(
            title=f"Suggestion de {message.author.display_name}",
            description=message.content,
            color=0xcbb5f1
        )
        embed_msg.set_footer(text=f"Suggestion #{suggestion_number}", icon_url=message.author.avatar.url if message.author.avatar else None)
        embed_msg.timestamp = message.created_at
        msg = await message.channel.send(embed=embed_msg)
        if message.attachments:
            embed_msg.set_image(url=message.attachments[0].url)
            await msg.edit(embed=embed_msg)
        for emoji in ["✅", "➖", "❌"]:
            await msg.add_reaction(emoji)
        new_values = {
            "suggestions.last_number": suggestion_number,
            f"suggestions.messages.{suggestion_number}": str(msg.id)
        }
        await suggestions_col.update_one(
            {"guildId": str(message.guild.id)},
            {"$set": new_values},
            upsert=True
        )

# Charger le COG
async def setup(bot: commands.Bot):
    await bot.add_cog(SuggestionsConfigCog(bot))
