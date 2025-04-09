import discord
from discord.ext import commands
from datetime import datetime

BOOST_CHANNEL_ID = 1348493920031604786
BOOST_IMAGE = "https://cdn.discordapp.com/attachments/1102406059722801184/1359660859978289284/85E1E65D-F685-4C47-988E-9BD653941572.png?ex=67f84a5a&is=67f6f8da&hm=20ab2d834ceeecb3fec7cc55f3c3056820288c7f61b73c516b2377994070c48c&"
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
        embed.set_footer(text="Lonely kurozen • Boost détecté automatiquement")

        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BoostAutoTask(bot))
    print("✅ BoostAutoTask bien enregistré comme cog.")
