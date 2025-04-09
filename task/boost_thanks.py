import discord
from discord.ext import commands
from datetime import datetime

BOOST_CHANNEL_ID = 1348493920031604786
BOOST_IMAGE = "https://cdn.discordapp.com/attachments/1102406059722801184/1359611493775179857/49777FF6-F8D2-4D28-9603-FB97490319D0.png?ex=67f81c60&is=67f6cae0&hm=23ed375a8ef12094313ac03d5856b68c4c3c6cb4fe85302914d984bd820cec2a&"
EMBED_COLOR = discord.Color.from_str("#DCCEF2")

class BoostAutoTask(commands.Cog, name="BoostAutoTask"):
    def __init__(self, bot):
        self.bot = bot
        print("[INIT] BoostAutoTask instancié")

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.premium_since != after.premium_since and after.premium_since is not None:
            print(f"[✅] {after.display_name} a boosté !")
            await self.send_boost_message(after)

    async def send_boost_message(self, booster: discord.Member):
        channel = booster.guild.get_channel(BOOST_CHANNEL_ID)
        if not channel:
            print(f"[⚠️] Channel introuvable : {BOOST_CHANNEL_ID}")
            return

        embed = discord.Embed(
            title="˖ ࣪⭑ 𝐁𝐎𝐎𝐒𝐓 𝐌𝐄𝐑𝐂𝐈 / 𝐓𝐇𝐀𝐍𝐊 𝐘𝐎𝐔 ˖ ࣪⭑",
            description=(
                f"💜 Merci {booster.mention} d’avoir boosté *lonely kurozen* !\n"
                f"→ Ton énergie alimente notre monde en magie violette ✨\n"
                f"✦ Grâce à toi, Kurozen veille avec encore plus de puissance cette nuit..."
            ),
            color=EMBED_COLOR,
            timestamp=datetime.utcnow()
        )
        embed.set_image(url=BOOST_IMAGE)
        embed.set_footer(text="NOCTÆ • Boost détecté automatiquement")

        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BoostAutoTask(bot))
    print("✅ BoostAutoTask bien enregistré comme cog.")
