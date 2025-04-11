import discord
from discord.ext import commands
import re
from datetime import datetime

# === CONFIGURATION ===
WHITELIST_ROLE_IDS = {
    1348427342179074162, 1353167649265160222, 1348208855263350805,
    1348211963888668734, 1353532487577370624, 1360309516746363063,
    1348428905832513607, 1351423658400284703, 1350913347444412416,
    1354938489308713142
}
LINK_REGEX = re.compile(r"(https?://|discord\.gg/|discord\.com/invite/)", re.IGNORECASE)
EMBED_COLOR = discord.Color.from_str("#DCCEF2")

class AntiLinkTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        if not LINK_REGEX.search(message.content):
            return  # aucun lien détecté

        # Check si l'auteur a un rôle whitelisté
        if any(role.id in WHITELIST_ROLE_IDS for role in message.author.roles):
            return  # rôle autorisé, on laisse passer

        try:
            await message.delete()
        except discord.Forbidden:
            return  # pas les perms pour delete

        embed = discord.Embed(
            description=f"🚫 {message.author.mention} — **Désolé**, tu ne possèdes pas de rôle whitelist pour publier des liens. C'est interdit ici !",
            color=EMBED_COLOR,
            timestamp=datetime.utcnow()
        )
        warn = await message.channel.send(embed=embed)
        await warn.delete(delay=5)

# === EXTENSION ===
async def setup(bot):
    await bot.add_cog(AntiLinkTask(bot))
