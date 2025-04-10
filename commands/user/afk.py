import discord
from discord.ext import commands
from discord import app_commands
from discord.utils import get
import os
import motor.motor_asyncio
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
client_mongo = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client_mongo[DATABASE_NAME]
afk_status = db["afk_status"]

class AFKCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # === COMMANDES ===
    @commands.command(name="afk")
    async def afk_prefix(self, ctx):
        await self.set_afk(ctx.author, ctx)

    @app_commands.command(name="afk", description="Passe en mode AFK (Away From Keyboard).")
    async def afk_slash(self, interaction: discord.Interaction):
        await self.set_afk(interaction.user, interaction)

    async def set_afk(self, member, ctx_or_inter):
        if await afk_status.find_one({"_id": member.id}):
            msg = "🚫 Tu es déjà en AFK."
        else:
            try:
                original_name = member.display_name
                afk_name = f"AFK | {original_name}"
                await member.edit(nick=afk_name)
                await afk_status.insert_one({
                    "_id": member.id,
                    "guild_id": member.guild.id,
                    "original_nick": original_name
                })
                msg = f"✅ Tu es maintenant AFK : `{afk_name}`"
            except discord.Forbidden:
                msg = "❌ Je n'ai pas la permission de changer ton pseudo."

        if isinstance(ctx_or_inter, commands.Context):
            await ctx_or_inter.send(msg)
        else:
            await ctx_or_inter.response.send_message(msg, ephemeral=True)

    # === RESTORE AUTO ===
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        await self.restore_if_afk(message.author, message.guild)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not before.channel and after.channel:
            await self.restore_if_afk(member, member.guild)

    async def restore_if_afk(self, member, guild):
        record = await afk_status.find_one({"_id": member.id, "guild_id": guild.id})
        if record:
            try:
                await member.edit(nick=record["original_nick"])
            except discord.Forbidden:
                pass
            await afk_status.delete_one({"_id": member.id})
            try:
                await member.send("🔔 Tu n'es plus AFK. Ton pseudo a été restauré.")
            except:
                pass

# === EXTENSION ===
async def setup(bot):
    await bot.add_cog(AFKCog(bot))
