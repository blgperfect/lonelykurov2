import os
import discord
from discord.ext import commands
from discord import app_commands
import motor.motor_asyncio
from dotenv import load_dotenv
from datetime import datetime

# === ENV
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

client_mongo = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client_mongo[DATABASE_NAME]
warns_col = db["warns"]

# === Channels
LOG_WARN_CHANNEL_ID = 1359617131645374636
LOG_MOD_CHANNEL_ID = 1359617112783716552


class WarnSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # === WARN (slash)
    @app_commands.command(name="warn", description="Avertir un membre")
    @app_commands.checks.has_permissions(kick_members=True)
    async def warn_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Aucune raison"):
        await self.process_warn(interaction, member, reason)

    async def process_warn(self, context, member: discord.Member, reason: str):
        author = context.user if isinstance(context, discord.Interaction) else context.author
        guild = context.guild

        if member.top_role >= author.top_role:
            embed = discord.Embed(
                title="⛔ Action refusée",
                description="Tu ne peux pas avertir ce membre, son rôle est égal ou supérieur au tien.",
                color=discord.Color.red()
            )
            if isinstance(context, discord.Interaction):
                await context.response.send_message(embed=embed, ephemeral=True)
            else:
                await context.send(embed=embed, delete_after=10)
            return

        data = await warns_col.find_one({"_id": member.id})
        warn_count = data["count"] if data else 0
        warn_count += 1

        # Warn 4 = Kick
        if warn_count >= 3:
            try:
                await member.send(
                    embed=discord.Embed(
                        title="🚫 Expulsion automatique",
                        description=(
                            f"Bonjour {member.name}, tu as reçu 3 avertissements sur **{guild.name}**, "
                            f"tu as donc été **expulsé automatiquement**."
                        ),
                        color=discord.Color.red()
                    )
                )
            except discord.Forbidden:
                pass

            await member.kick(reason="Avertissements cumulés (3)")
            await warns_col.delete_one({"_id": member.id})

            embed = discord.Embed(
                title="🚫 Membre expulsé automatiquement",
                description=f"{member.mention} a été **kick** après 3 avertissements.",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="👮 Par", value=author.mention)
            embed.add_field(name="📄 Dernière raison", value=reason)

            for cid in [LOG_MOD_CHANNEL_ID, LOG_WARN_CHANNEL_ID]:
                log_channel = guild.get_channel(cid)
                if log_channel:
                    await log_channel.send(embed=embed)

            if isinstance(context, discord.Interaction):
                await context.response.send_message(embed=embed, ephemeral=True)
            else:
                await context.send(embed=embed)
            return

        # Enregistrer le warn
        await warns_col.update_one({"_id": member.id}, {"$set": {"count": warn_count}}, upsert=True)

        embed = discord.Embed(
            title="⚠️ Avertissement",
            description=(
                f"{member.mention} a été averti.\n"
                f"Nombre actuel d'avertissements : **{warn_count}**\n\n"
                f"Raison : {reason}"
            ),
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Warn System")

        # Log
        warn_log = guild.get_channel(LOG_WARN_CHANNEL_ID)
        if warn_log:
            await warn_log.send(embed=embed)

        if isinstance(context, discord.Interaction):
            await context.response.send_message(embed=embed, ephemeral=True)
        else:
            await context.send(embed=embed)

    # === !warns / /warns
    @app_commands.command(name="warns", description="Voir le nombre d'avertissements d'un membre")
    @app_commands.checks.has_permissions(kick_members=True)
    async def warns_slash(self, interaction: discord.Interaction, member: discord.Member):
        await self.show_warns(interaction, member)

    async def show_warns(self, context, member: discord.Member):
        data = await warns_col.find_one({"_id": member.id})
        count = data["count"] if data else 0

        embed = discord.Embed(
            title=f"📊 Warns de {member.name}",
            description=f"{member.mention} a actuellement **{count}** avertissement(s).",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )

        if isinstance(context, discord.Interaction):
            await context.response.send_message(embed=embed, ephemeral=True)
        else:
            await context.send(embed=embed)

    # === !resetwarns / /resetwarns

    @app_commands.command(name="resetwarns", description="Réinitialiser les warns d’un membre")
    @app_commands.checks.has_permissions(ban_members=True)
    async def resetwarns_slash(self, interaction: discord.Interaction, member: discord.Member):
        await self.reset_warns(interaction, member)

    async def reset_warns(self, context, member: discord.Member):
        await warns_col.delete_one({"_id": member.id})
        embed = discord.Embed(
            title="🔄 Warns réinitialisés",
            description=f"Les avertissements de {member.mention} ont été supprimés.",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )

        if isinstance(context, discord.Interaction):
            await context.response.send_message(embed=embed, ephemeral=True)
        else:
            await context.send(embed=embed)

    # === !warnlist / /warnlist

    @app_commands.command(name="warnlist", description="Afficher tous les utilisateurs avertis")
    @app_commands.checks.has_permissions(ban_members=True)
    async def warnlist_slash(self, interaction: discord.Interaction):
        await self.list_warns(interaction)

    async def list_warns(self, context):
        results = warns_col.find()
        lines = []
        async for doc in results:
            user = self.bot.get_user(doc["_id"])
            name = user.mention if user else f"ID `{doc['_id']}`"
            lines.append(f"{name} — {doc['count']} warns")

        embed = discord.Embed(
            title="📚 Liste des avertissements",
            description="\n".join(lines) if lines else "Aucun utilisateur averti.",
            color=discord.Color.purple(),
            timestamp=datetime.utcnow()
        )

        if isinstance(context, discord.Interaction):
            await context.response.send_message(embed=embed, ephemeral=True)
        else:
            await context.send(embed=embed)

# === Setup
async def setup(bot):
    await bot.add_cog(WarnSystem(bot))
