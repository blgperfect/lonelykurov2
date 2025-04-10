import discord
from discord.ext import commands
from discord import app_commands
import motor.motor_asyncio
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = mongo_client["kurozen_system"]  # ✅ fix ici
presentation_coll = db["presentations"]
config_coll = db["presentation_configs"]


# 📄 Modèle brut envoyé dans le salon
PRESENTATION_TEMPLATE = (
    "╔═౨ৎ  **IDENTITÉ**\n"
    "╠ **Prénom** :\n"
    "╠ **Surnom** :\n"
    "╠ **Âge** :\n"
    "╠ **Origine** :\n"
    "╠ **Région** :\n"
    "╠ **Profession** :\n"
    "╠ **Signe astrologique** :\n"
    "╠ **Situation** :\n"
    "╠ **Recherche** :\n"
    "╚═౨ৎ\n\n"
    "╔౨ৎ  **PERSONNALITÉ**\n"
    "╠ **Traits positifs** :\n"
    "╠ **Traits négatifs** :\n"
    "╠ **Aime** :\n"
    "╠ **Déteste** :\n"
    "╚═౨ৎ\n\n"
    "╔౨ৎ  **PHYSIQUE**\n"
    "╠ **Taille** :\n"
    "╠ **Couleur de yeux** :\n"
    "╠ **Couleur de cheveux** :\n"
    "╚═౨ৎ"
)

class PresentationModal(discord.ui.Modal, title="✏️ Écris ta présentation"):
    def __init__(self, user, guild, mode="create"):
        super().__init__()
        self.user = user
        self.guild = guild
        self.mode = mode

        self.presentation = discord.ui.TextInput(
            label="Ta présentation",
            style=discord.TextStyle.paragraph,
            max_length=1000,
            required=True,
            placeholder="Présente-toi en 1000 caractères max..."
        )
        self.add_item(self.presentation)

    async def on_submit(self, interaction: discord.Interaction):
        content = self.presentation.value[:1000]
        query = {"user_id": str(self.user.id), "guild_id": str(self.guild.id)}
        existing = await presentation_coll.find_one(query, sort=[("date", -1)])

        if self.mode == "create" and existing:
            await interaction.response.send_message("❌ Tu as déjà une présentation. Utilise modifier.", ephemeral=True)
            return
        if self.mode == "modify" and not existing:
            await interaction.response.send_message("❌ Aucune présentation trouvée à modifier.", ephemeral=True)
            return

        data = {
            "user_id": str(self.user.id),
            "guild_id": str(self.guild.id),
            "presentation": content,
            "date": datetime.utcnow()
        }

        if self.mode == "create":
            await presentation_coll.insert_one(data)
            msg = "✅ Présentation créée avec succès !"
        else:
            await presentation_coll.update_one({"_id": existing["_id"]}, {"$set": data})
            msg = "✅ Présentation modifiée avec succès !"

        await interaction.response.send_message(msg, ephemeral=True)

        config = await config_coll.find_one({"guild_id": str(self.guild.id)})
        if config and config.get("active") and config.get("channel_id"):
            channel = self.guild.get_channel(int(config["channel_id"]))
            if channel:
                embed = discord.Embed(
                    title=f"Présentation de {self.user.display_name}",
                    description=content,
                    color=discord.Color.blue() if self.mode == "create" else discord.Color.green(),
                    timestamp=datetime.utcnow()
                )
                embed.set_footer(text="Présentation automatique")
                await channel.send(content=f"{self.user.mention}", embed=embed)

class PresentationView(discord.ui.View):
    def __init__(self, user: discord.User, guild: discord.Guild):
        super().__init__(timeout=120)
        self.user = user
        self.guild = guild

    @discord.ui.button(label="📝 Créer", style=discord.ButtonStyle.primary)
    async def create(self, interaction: discord.Interaction, _):
        if interaction.user != self.user:
            return await interaction.response.send_message("❌ Pas pour toi !", ephemeral=True)
        await interaction.response.send_modal(PresentationModal(self.user, self.guild, mode="create"))

    @discord.ui.button(label="🛠️ Modifier", style=discord.ButtonStyle.success)
    async def modify(self, interaction: discord.Interaction, _):
        if interaction.user != self.user:
            return await interaction.response.send_message("❌ Pas pour toi !", ephemeral=True)
        await interaction.response.send_modal(PresentationModal(self.user, self.guild, mode="modify"))

    @discord.ui.button(label="👀 Afficher", style=discord.ButtonStyle.secondary)
    async def view(self, interaction: discord.Interaction, _):
        if interaction.user != self.user:
            return await interaction.response.send_message("❌ Pas pour toi !", ephemeral=True)
        query = {"user_id": str(self.user.id), "guild_id": str(self.guild.id)}
        pres = await presentation_coll.find_one(query, sort=[("date", -1)])
        if not pres:
            return await interaction.response.send_message("❌ Aucune présentation trouvée.", ephemeral=True)
        embed = discord.Embed(
            title=f"Présentation de {self.user.display_name}",
            description=pres["presentation"],
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="📄 Modèle", style=discord.ButtonStyle.secondary)
    async def template(self, interaction: discord.Interaction, _):
        if interaction.user != self.user:
            return await interaction.response.send_message("❌ Pas pour toi !", ephemeral=True)
        await interaction.response.send_message(PRESENTATION_TEMPLATE, ephemeral=True)

class PresentationUI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="presentation", description="Menu interactif de présentation")
    async def presentation(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message("Commande serveur uniquement.", ephemeral=True)
        embed = discord.Embed(
            title="🎭 Menu Présentation",
            description="Choisis une action : 📝 Créer, 🛠️ Modifier, 👀 Afficher, 📄 Modèle",
            color=discord.Color.blurple()
        )
        view = PresentationView(interaction.user, interaction.guild)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="presentationconfig", description="Configure le salon des présentations (admin)")
    @app_commands.describe(channel="Salon où envoyer les présentations")
    async def presentationconfig(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Tu dois être admin.", ephemeral=True)

        await config_coll.update_one(
            {"guild_id": str(interaction.guild.id)},
            {"$set": {
                "channel_id": str(channel.id),
                "guild_id": str(interaction.guild.id),
                "active": True
            }},
            upsert=True
        )

        await interaction.response.send_message(f"✅ Salon configuré : {channel.mention}", ephemeral=True)

        # Envoi du message d'accueil + épinglage
        intro = f"👋 Bienvenue dans le salon des présentations de **{interaction.guild.name}** !\n\n" \
                "Tu peux utiliser la commande `/presentation` pour créer ou modifier ta présentation. " \
                "Une fois créée, elle sera automatiquement publiée ici."
        intro_message = await channel.send(intro)
        await channel.send(PRESENTATION_TEMPLATE)
        try:
            await intro_message.pin()
        except discord.Forbidden:
            await channel.send("⚠️ Je n'ai pas la permission d'épingler ce message.")

async def setup(bot: commands.Bot):
    await bot.add_cog(PresentationUI(bot))
