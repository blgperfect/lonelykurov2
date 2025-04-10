import os
import discord
from discord.ext import commands
from discord import app_commands
import motor.motor_asyncio
from dotenv import load_dotenv

# === ENV & MONGO ===
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DATABASE_NAME]
tempvoc_col = db["tempvoc_configs"]

class VocTemp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup-voc-temp", description="Configure les salons vocaux temporaires")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_voc_temp(self, interaction: discord.Interaction):
        guild = interaction.guild

        # Vérifie si on a déjà une config
        config = await tempvoc_col.find_one({"guild_id": guild.id})
        category = guild.get_channel(config["category_id"]) if config else None
        hub = guild.get_channel(config["hub_channel_id"]) if config else None

        # Recrée uniquement si supprimés
        if category is None:
            category = await guild.create_category("🌀 Vocaux temporaires")

        if hub is None:
            hub = await guild.create_voice_channel("➕ Créer ton salon voc", category=category)

        # Sauvegarde par ID uniquement
        await tempvoc_col.update_one(
            {"guild_id": guild.id},
            {"$set": {"hub_channel_id": hub.id, "category_id": category.id}},
            upsert=True
        )

        await interaction.response.send_message(
            f"✅ Configuration enregistrée !\n**Salon hub** : {hub.mention}\n**Catégorie** : {category.name}", ephemeral=True
        )

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot or not member.guild:
            return

        config = await tempvoc_col.find_one({"guild_id": member.guild.id})
        if not config:
            return

        hub_id = config["hub_channel_id"]
        category_id = config["category_id"]

        # Si membre rejoint le salon hub
        if after.channel and after.channel.id == hub_id:
            category = member.guild.get_channel(category_id)
            overwrites = {
                member.guild.default_role: discord.PermissionOverwrite(connect=True),
                member: discord.PermissionOverwrite(
                    connect=True, manage_channels=True, manage_roles=True, mute_members=True, move_members=True
                )
            }
            temp_voc = await member.guild.create_voice_channel(
                name=f"🔊 Salon de {member.display_name}",
                category=category,
                overwrites=overwrites
            )
            await member.move_to(temp_voc)

        # Suppression du salon s’il est vide (sauf hub)
        if before.channel and before.channel.category_id == category_id:
            if before.channel.id != hub_id and len(before.channel.members) == 0:
                try:
                    await before.channel.delete()
                except Exception as e:
                    print(f"Erreur suppression salon : {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(VocTemp(bot))
