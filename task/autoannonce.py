import discord
from discord.ext import commands
from datetime import datetime

# === CONFIGURATION ===
CHANNEL_ID = 1353173975102001222  # salon dédié aux annonces
ROLE_ID = 1348573200702898220     # rôle à mentionner
EMBED_COLOR = discord.Color.from_str("#DCCEF2")  # mauve pastel clair

class AutoAnnonce(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        # On ne s'active que dans le salon prévu
        if message.channel.id != CHANNEL_ID:
            return

        # Si l'utilisateur n'est pas admin, on supprime + message d'erreur
        if not message.author.guild_permissions.administrator:
            await message.delete()
            await message.channel.send(
                f"🚫 {message.author.mention}, seuls les **admins** peuvent poster ici.",
                delete_after=5
            )
            return

        # On supprime le message original
        content = message.content
        await message.delete()

        # Création de l'embed
        embed = discord.Embed(
            title="✦ Kurozen • 𝐀𝐍𝐍𝐎𝐍𝐂𝐄 | 𝐀𝐍𝐍𝐎𝐔𝐍𝐂𝐄𝐌𝐄𝐍𝐓",
            description=content,
            color=EMBED_COLOR,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Kurozen Bot • Posté par {message.author.display_name}")

        # Envoi de l'annonce finale
        await message.channel.send(
            content=f"<@&{ROLE_ID}>",
            embed=embed
        )

# === EXTENSION ===
async def setup(bot):
    await bot.add_cog(AutoAnnonce(bot))
