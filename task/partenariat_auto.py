import discord
from discord.ext import commands
from datetime import datetime
import re
import motor.motor_asyncio
import os
from dotenv import load_dotenv

# === CONFIGURATION ===
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)

db = client_mongo[DATABASE_NAME]
scores_col = db["partenariat_scores"]

CHANNEL_ID = 1349081996542087168  # Salon de partenariat
ROLE_ID = 1353155776058753154     # Rôle à mentionner
EMBED_COLOR = discord.Color.from_str("#FFBEE8")  # Rose pastel
EMBED_IMAGE_URL = "https://cdn.discordapp.com/attachments/1102406059722801184/1359676329607565503/203A3ECB-96AE-489A-A84B-4F02F8AD5900.png?ex=67f858c2&is=67f70742&hm=4929dbe2575d0ebb765593192a66b4856aadac5a245164fe5abdf59ff1fc6a49&"

class AutoPartenariat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        if message.channel.id != CHANNEL_ID:
            return

        # Vérifie présence d’un lien d’invitation Discord
        if not re.search(r"https?://(www\.)?discord\.gg/[\w-]+", message.content):
            return

        # === Incrémentation du score dans MongoDB
        user_id = str(message.author.id)
        guild_id = message.guild.id
        doc = await scores_col.find_one({"guild_id": guild_id, "user_id": user_id})
        score = (doc.get("score", 0) + 1) if doc else 1
        if doc:
            await scores_col.update_one({"guild_id": guild_id, "user_id": user_id}, {"$set": {"score": score}})
        else:
            await scores_col.insert_one({"guild_id": guild_id, "user_id": user_id, "score": score})


        # === Texte personnalisé FR
        msg = (
            f"Merci {message.author.mention} pour ce partenariat ! <a:LH_PIKA_MUSIQUE:1358568878879281242> \n"
            f"**{message.guild.name}** est heureux de te compter parmi nous !\n"
            f"<:1_1symbol_yes:1359109347812048958>  Tu as présentement **{score}** partenariat{'s' if score > 1 else ''} fait pour nous !\n"
            f"<:love:1348213329591664731>  Nous sommes actuellement **{message.guild.member_count}** membres !"
        )

        embed = discord.Embed(
            title="🤝 Partenariat détecté",
            description=msg,
            color=EMBED_COLOR,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Par : {message.author.display_name}")
        embed.set_image(url=EMBED_IMAGE_URL)

        role = message.guild.get_role(ROLE_ID)
        mention = role.mention if role else ""

        await message.channel.send(content=mention, embed=embed)

# === EXTENSION ===
async def setup(bot):
    await bot.add_cog(AutoPartenariat(bot))
