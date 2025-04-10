import discord, re, os
from discord.ext import commands
from discord import app_commands
import motor.motor_asyncio
from dotenv import load_dotenv

# === CONFIGURATION RAPIDE === #
REACTION_YES = "<:1887likebluepurple:1359679917771456733>"
REACTION_NO = "<:1887crossbluepurple:1359679961803526184>"

# === DB SETUP ===
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DATABASE_NAME]
reaction_collection = db["reaction_channels"]
thread_collection = db["thread_configs"]

# === UI PANEL VIEW === #
class ConfigPanelView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.add_item(ConfigButton("➕ Ajouter réactions", "add_react"))
        self.add_item(ConfigButton("➖ Retirer réactions", "remove_react"))
        self.add_item(ConfigButton("👁️ Voir réactions", "view_react"))
        self.add_item(ConfigButton("➕ Ajouter threads", "add_thread"))
        self.add_item(ConfigButton("➖ Retirer threads", "remove_thread"))
        self.add_item(ConfigButton("👁️ Voir threads", "view_thread"))

class ConfigButton(discord.ui.Button):
    def __init__(self, label, custom_id):
        super().__init__(label=label, style=discord.ButtonStyle.primary, custom_id=custom_id)

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("🚫 Réservé aux administrateurs.", ephemeral=True)

        col, kind = (reaction_collection, "réactions") if "react" in self.custom_id else (thread_collection, "threads")
        guild_id = interaction.guild.id
        doc = await col.find_one({"guild_id": guild_id})
        current = doc.get("channels", []) if doc else []

        if self.custom_id.startswith("view"):
            if not current:
                return await interaction.response.send_message(f"📭 Aucun salon configuré pour les {kind}.", ephemeral=True)
            salon_list = "\n".join(f"<#{cid}>" for cid in current)
            embed = discord.Embed(
                title=f"Salons configurés pour les {kind}",
                description=salon_list,
                color=discord.Color.blurple()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        # Demande à l'utilisateur de mentionner les salons
        await interaction.response.send_message("Mentionnez les salons (ex: #général #logs)", ephemeral=True)

        def check(m): return m.author == interaction.user and m.channel == interaction.channel
        try:
            msg = await interaction.client.wait_for("message", timeout=30.0, check=check)
            channel_ids = [int(i) for i in re.findall(r"<#(\d+)>", msg.content)]
            if not channel_ids:
                return await interaction.followup.send("❌ Aucun salon détecté.", ephemeral=True)

            if self.custom_id.startswith("add"):
                updated = list(set(current + channel_ids))
                await upsert_collection(col, guild_id, updated)
                added = [cid for cid in channel_ids if cid not in current]
                if added:
                    chs = ", ".join(f"<#{c}>" for c in added)
                    return await interaction.followup.send(f"✅ Ajouté aux {kind} : {chs}", ephemeral=True)
                return await interaction.followup.send(f"Aucun nouveau salon ajouté aux {kind}.", ephemeral=True)

            elif self.custom_id.startswith("remove"):
                removed = [cid for cid in channel_ids if cid in current]
                updated = [cid for cid in current if cid not in channel_ids]
                await upsert_collection(col, guild_id, updated)
                msg_parts = []
                if removed:
                    msg_parts.append(f"✅ Retiré de {kind} : {', '.join(f'<#{c}>' for c in removed)}")
                else:
                    msg_parts.append(f"❌ Aucun de ces salons n'était configuré pour les {kind}.")
                return await interaction.followup.send("\n".join(msg_parts), ephemeral=True)

        except Exception:
            return await interaction.followup.send("⏰ Temps écoulé ou erreur lors de la configuration.", ephemeral=True)

async def upsert_collection(col, guild_id, updated_list):
    if await col.find_one({"guild_id": guild_id}):
        await col.update_one({"guild_id": guild_id}, {"$set": {"channels": updated_list}})
    else:
        await col.insert_one({"guild_id": guild_id, "channels": updated_list})

# === COG PRINCIPAL === #
class ConfigMenu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="config_salon_menu", description="Panneau de configuration (réactions & threads auto)")
    @app_commands.checks.has_permissions(administrator=True)
    async def config_menu(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🛠️ Panneau de Configuration",
            description="• Gérez les **réactions automatiques** et **threads auto**\n• Cliquez sur un bouton pour configurer",
            color=discord.Color.dark_blue()
        )
        await interaction.response.send_message(embed=embed, view=ConfigPanelView(self.bot))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        # Ajout auto des réactions
        data = await reaction_collection.find_one({"guild_id": message.guild.id})
        if data and message.channel.id in data.get("channels", []):
            try:
                await message.add_reaction(REACTION_YES)
                await message.add_reaction(REACTION_NO)
            except:
                pass

        # Création automatique de thread
        data = await thread_collection.find_one({"guild_id": message.guild.id})
        if data and message.channel.id in data.get("channels", []):
            try:
                name = message.content[:50].strip() or "Discussion"
                await message.create_thread(name=name)
            except:
                pass

# === SETUP === #
async def setup(bot: commands.Bot):
    await bot.add_cog(ConfigMenu(bot))