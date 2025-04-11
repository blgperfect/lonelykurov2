import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timedelta
import asyncio
import motor.motor_asyncio
import os
from dotenv import load_dotenv

# === MONGO SETUP ===
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DATABASE_NAME]
mute_col = db["mute_records"]

# === CONFIG ===
MUTE_ROLE_ID = 1352061172869894175
LOG_CHANNEL_ID = 1360091869622702303

def parse_duration(duration_str):
    unit = duration_str[-1]
    try:
        value = int(duration_str[:-1])
    except ValueError:
        return None
    if unit == "s":
        return timedelta(seconds=value)
    elif unit == "m":
        return timedelta(minutes=value)
    elif unit == "h":
        return timedelta(hours=value)
    elif unit == "d":
        return timedelta(days=value)
    return None

class MuteManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.unmute_loop.start()

    def cog_unload(self):
        self.unmute_loop.cancel()

    async def send_log(self, guild, user, moderator, action, reason, duration=None):
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if not log_channel:
            return

        embed = discord.Embed(
            title=f"🔇 {action} | Mute System",
            color=discord.Color.orange() if action == "Mute" else discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="👤 Membre", value=f"{user.mention} (`{user.id}`)", inline=False)
        embed.add_field(name="🛡️ Modérateur", value=f"{moderator.mention}", inline=False)
        embed.add_field(name="📝 Raison", value=reason or "Non spécifiée", inline=False)
        if duration:
            embed.add_field(name="⏰ Durée", value=duration, inline=False)
        embed.set_footer(text="Kurozen Bot • Mute Log")
        await log_channel.send(embed=embed)

    @app_commands.command(name="mute", description="Mute un membre pour une durée donnée.")
    @app_commands.describe(member="Membre à mute", duration="Ex: 10m, 1h, 2d", reason="Raison du mute")
    async def mute(self, interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = None):
        if not interaction.user.guild_permissions.manage_roles:
            return await interaction.response.send_message("❌ Permission requise : gérer les rôles.", ephemeral=True)

        mute_role = interaction.guild.get_role(MUTE_ROLE_ID)
        if not mute_role:
            return await interaction.response.send_message("❌ Rôle de mute introuvable.", ephemeral=True)

        if mute_role in member.roles:
            return await interaction.response.send_message("⚠️ Ce membre est déjà mute.", ephemeral=True)

        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌ Ce membre a un rôle égal ou supérieur au tien.", ephemeral=True)

        delta = parse_duration(duration)
        if not delta:
            return await interaction.response.send_message("❌ Durée invalide. Utilise par ex: `10m`, `1h`, `1d`", ephemeral=True)

        roles_to_remove = [
            role for role in member.roles 
            if role != interaction.guild.default_role and not role.managed and role != mute_role
        ]
        role_ids = [r.id for r in roles_to_remove]

        try:
            await member.remove_roles(*roles_to_remove, reason="Mute temporaire")
            await member.add_roles(mute_role, reason=reason)
        except discord.Forbidden:
            return await interaction.response.send_message("❌ Impossible de modifier les rôles du membre (hiérarchie ou permissions).", ephemeral=True)

        end_time = datetime.utcnow() + delta

        await mute_col.insert_one({
            "guild_id": str(interaction.guild.id),
            "user_id": str(member.id),
            "unmute_at": end_time,
            "previous_roles": role_ids
        })

        await self.send_log(interaction.guild, member, interaction.user, "Mute", reason, duration)
        await interaction.response.send_message(f"✅ {member.mention} a été mute pour `{duration}`.")

    @app_commands.command(name="unmute", description="Unmute un membre manuellement.")
    @app_commands.describe(member="Membre à unmute")
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        if not interaction.user.guild_permissions.manage_roles:
            return await interaction.response.send_message("❌ Permission requise : gérer les rôles.", ephemeral=True)

        mute_role = interaction.guild.get_role(MUTE_ROLE_ID)
        if not mute_role or mute_role not in member.roles:
            return await interaction.response.send_message("⚠️ Ce membre n’est pas mute.", ephemeral=True)

        record = await mute_col.find_one({"guild_id": str(interaction.guild.id), "user_id": str(member.id)})

        try:
            await member.remove_roles(mute_role, reason="Unmute manuel")
            if record:
                previous_roles = [interaction.guild.get_role(int(rid)) for rid in record.get("previous_roles", [])]
                previous_roles = [r for r in previous_roles if r is not None]
                await member.add_roles(*previous_roles, reason="Rôles restaurés après mute")
            await mute_col.delete_many({"guild_id": str(interaction.guild.id), "user_id": str(member.id)})
        except Exception as e:
            return await interaction.response.send_message(f"❌ Erreur : {e}", ephemeral=True)

        await self.send_log(interaction.guild, member, interaction.user, "Unmute", reason="Manuel")
        await interaction.response.send_message(f"✅ {member.mention} a été unmute.")

    @tasks.loop(minutes=1)
    async def unmute_loop(self):
        now = datetime.utcnow()
        async for record in mute_col.find({"unmute_at": {"$lte": now}}):
            guild = self.bot.get_guild(int(record["guild_id"]))
            if not guild:
                continue
            member = guild.get_member(int(record["user_id"]))
            mute_role = guild.get_role(MUTE_ROLE_ID)
            if member and mute_role in member.roles:
                try:
                    await member.remove_roles(mute_role, reason="Mute expiré")
                    previous_roles = [
                        guild.get_role(int(rid)) for rid in record.get("previous_roles", [])
                    ]
                    previous_roles = [r for r in previous_roles if r is not None]
                    await member.add_roles(*previous_roles, reason="Rôles restaurés après mute")
                    await self.send_log(guild, member, self.bot.user, "Unmute", "Automatique (fin du mute)")
                except:
                    pass
            await mute_col.delete_one({"_id": record["_id"]})

    @unmute_loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

# === EXTENSION ===
async def setup(bot: commands.Bot):
    await bot.add_cog(MuteManager(bot))
