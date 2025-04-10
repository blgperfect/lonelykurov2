import os, asyncio, discord, motor.motor_asyncio
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

client_mongo = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client_mongo[DATABASE_NAME]
voc_stats_col = db["voc_stats"]

# --------------------------------------------------
# Menu de sélection pour les catégories
# --------------------------------------------------
class CategorySelect(discord.ui.Select):
    def __init__(self, guild: discord.Guild):
        options = [
            discord.SelectOption(label="Aucune", value="none", description="Pas de catégorie")
        ]
        for category in guild.categories:
            options.append(discord.SelectOption(label=category.name, value=str(category.id)))
        super().__init__(
            placeholder="Sélectionnez une catégorie",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        selected_value = self.values[0]
        category = None
        if selected_value != "none":
            category = interaction.guild.get_channel(int(selected_value))
        
        # Supprimer les anciens salons s'ils existent
        doc = await voc_stats_col.find_one({"guildId": str(interaction.guild.id)})
        if doc and "channels" in doc:
            for ch in doc["channels"]:
                c = interaction.guild.get_channel(int(ch["channelId"]))
                if c:
                    await c.delete()
        
        def create_channel(name):
            return interaction.guild.create_voice_channel(
                name=name,
                category=category,
                overwrites={
                    interaction.guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=True)
                }
            )
        
        members = [m for m in interaction.guild.members if not m.bot]
        bots = [m for m in interaction.guild.members if m.bot]
        
        ch_humain = await create_channel(f"👤 Membres : {len(members)}")
        ch_bots  = await create_channel(f"🤖 Bots : {len(bots)}")
        ch_total = await create_channel(f"📊 Total : {len(interaction.guild.members)}")
        
        await voc_stats_col.update_one(
            {"guildId": str(interaction.guild.id)},
            {"$set": {
                "categoryId": str(category.id) if category else None,
                "channels": [
                    {"type": "humain", "channelId": str(ch_humain.id)},
                    {"type": "bot", "channelId": str(ch_bots.id)},
                    {"type": "total", "channelId": str(ch_total.id)},
                ]
            }},
            upsert=True
        )
        
        await interaction.response.send_message("✅ Salons statistiques créés.", ephemeral=True)

class CategorySelectView(discord.ui.View):
    def __init__(self, guild: discord.Guild):
        super().__init__(timeout=60)
        self.add_item(CategorySelect(guild))

# --------------------------------------------------
# Vue principale pour les statistiques vocales
# --------------------------------------------------
class VocStatsView(discord.ui.View):
    def __init__(self, bot: commands.Bot, guild_id: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.guild_id = str(guild_id)

    @discord.ui.button(label="➕ Créer", style=discord.ButtonStyle.success, custom_id="voc_create")
    async def create_voc_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Envoie du menu de sélection pour choisir la catégorie
        await interaction.response.send_message(
            "Sélectionnez une catégorie pour les salons vocaux (choisissez 'Aucune' si vous ne souhaitez pas de catégorie) :",
            ephemeral=True,
            view=CategorySelectView(interaction.guild)
        )

    @discord.ui.button(label="🗑 Supprimer", style=discord.ButtonStyle.danger, custom_id="voc_delete")
    async def delete_voc_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Tape `oui` pour confirmer.", ephemeral=True)

        def check(msg):
            return msg.author.id == interaction.user.id and msg.channel == interaction.channel and msg.content.lower() == "oui"

        try:
            await interaction.client.wait_for("message", check=check, timeout=30)
            doc = await voc_stats_col.find_one({"guildId": self.guild_id})
            if doc and "channels" in doc:
                for ch in doc["channels"]:
                    channel = interaction.guild.get_channel(int(ch["channelId"]))
                    if channel:
                        await channel.delete()
                await voc_stats_col.delete_one({"guildId": self.guild_id})
                await interaction.followup.send("✅ Salons supprimés.", ephemeral=True)
            else:
                await interaction.followup.send("Aucun salon à supprimer.", ephemeral=True)
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ Temps écoulé.", ephemeral=True)

# --------------------------------------------------
# Cog pour la commande /voc-stats
# --------------------------------------------------
class VocStatsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.update_stats.start()

    @app_commands.command(name="voc-stats", description="Gérer les salons vocaux de statistiques")
    async def voc_stats(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Vous devez être administrateur pour utiliser cette commande.",
                ephemeral=True
            )
            return
        embed = discord.Embed(
            title="Statistiques Vocales",
            description="Gérez ici les salons vocaux qui affichent des statistiques en temps réel.",
            color=0x1abc9c
        )
        embed.set_footer(text="Salons vocaux statistiques")
        await interaction.response.send_message(embed=embed, view=VocStatsView(self.bot, interaction.guild.id), ephemeral=True)

    @tasks.loop(minutes=5)
    async def update_stats(self):
        await self.bot.wait_until_ready()
        guilds = await voc_stats_col.find({}).to_list(length=None)
        for doc in guilds:
            guild = self.bot.get_guild(int(doc["guildId"]))
            if not guild:
                continue
            members = [m for m in guild.members if not m.bot]
            bots = [m for m in guild.members if m.bot]
            total = len(guild.members)

            for ch in doc.get("channels", []):
                channel = guild.get_channel(int(ch["channelId"]))
                if not channel:
                    continue
                if ch["type"] == "humain":
                    await channel.edit(name=f"👤 Membres : {len(members)}")
                elif ch["type"] == "bot":
                    await channel.edit(name=f"🤖 Bots : {len(bots)}")
                elif ch["type"] == "total":
                    await channel.edit(name=f"📊 Total : {total}")

async def setup(bot: commands.Bot):
    await bot.add_cog(VocStatsCog(bot))