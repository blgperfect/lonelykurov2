import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, button
from datetime import datetime
import motor.motor_asyncio
import os
from dotenv import load_dotenv
import pytz
import aiohttp

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DATABASE_NAME]
tickets_collection = db["tickets"]

TICKET_CATEGORY_ID = 1350920600117575760
LOG_CHANNEL_ID = 1359748159869292614
EMBED_COLOR = discord.Color.from_str("#C9B6D9")
EMBED_IMAGE_URL = "https://cdn.discordapp.com/attachments/1102406059722801184/1360006645442416690/66D6175D-7B11-4F64-AEA1-5EA905086CBC.png?ex=67f98c63&is=67f83ae3&hm=cd0e0eb728f272132212f31b2a627860ce3b86099d2282c7e71ced08a7c8f696&"
TIMEZONE = pytz.timezone("Europe/Paris")

ROLES = {
    "urgence": 1350913347444412416,
    "partenariat": 1348428905832513607,
    "autre": 1348427864533504102,
    "mod": 1348208855263350805,
    "ecoute": 1351423658400284703,
    "admin_mentions": [1348427342179074162, 1353167649265160222],
    "propartenaire": 1348427864533504102,
}

TICKETS = {
    "urgence": {
        "label": "💔 Urgence émotionnelle",
        "title": "Urgence émotionnelle",
        "message": "Coucou, on sait que tu ne vas pas bien... Raconte-nous un peu ce qui se passe 💜 L'équipe d'écoute va bientôt arriver pour t’écouter.",
        "role": ROLES["urgence"],
    },
    "partenariat": {
        "label": "🤝 Partenariat",
        "title": "Partenariat avec nous !",
        "message": "Merci d'avoir pensé à nous pour un partenariat ! Sois sûr d’avoir lu <#1354942165096333533>. Envoie ton lien et ta pub si tu remplis les conditions. L’équipe partenariat reviendra vers toi bientôt.",
        "role": ROLES["partenariat"],
    },
    "autre": {
        "label": "📌 Autre demande",
        "title": "Autre !",
        "message": "Merci d’avoir ouvert un ticket ! Explique-nous pourquoi tu as ouvert ce ticket ^^ Les modérateurs te répondront sous peu.",
        "role": ROLES["autre"],
    },
    "admin": {
        "label": "🛡️ Administrateur",
        "title": "Application administrateur !",
        "message": "Merci d’avoir ouvert un ticket ! Merci de répondre à ces questions :\n- Ton expérience ?\n- Tes disponibilités ?\n- Pourquoi veux-tu être staff ?\n- Ton âge ?\n- Ce que tu peux apporter ?",
        "mentions": ROLES["admin_mentions"],
        "role": None,
    },
    "mod": {
        "label": "🧹 Modérateur",
        "title": "Application modérateur !",
        "message": "Merci d’avoir ouvert un ticket ! Merci de répondre à ces questions :\n- Ton expérience ?\n- Tes disponibilités ?\n- Pourquoi veux-tu être staff ?\n- Ton âge ?\n- Ce que tu peux apporter ?",
        "role": ROLES["mod"],
    },
    "ecoute": {
        "label": "👂 Équipe Écoute",
        "title": "Application équipe écoute !",
        "message": "Merci d’avoir ouvert un ticket ! Merci de répondre à ces questions :\n- Ton expérience ?\n- Tes disponibilités ?\n- Pourquoi veux-tu être staff ?\n- Ton âge ?\n- Ce que tu peux apporter ?",
        "role": ROLES["ecoute"],
    },
    "propartenaire": {
        "label": "📢 Pro du partenariat",
        "title": "Application pro du partenariat !",
        "message": "Merci d’avoir ouvert un ticket ! Merci de répondre à ces questions :\n- Ton expérience ?\n- Tes disponibilités ?\n- Pourquoi veux-tu être staff ?\n- Ton âge ?\n- Ce que tu peux apporter ?",
        "role": ROLES["propartenaire"],
    },
}

class TicketView(View):
    def __init__(self, ticket_keys):
        super().__init__(timeout=None)
        for key in ticket_keys:
            self.add_item(Button(label=TICKETS[key]["label"], style=discord.ButtonStyle.primary, custom_id=key))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True

class MainTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="🎫 Autres demandes", style=discord.ButtonStyle.secondary, custom_id="main_autres")
    async def autres(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Choisis une option :", view=TicketView(["urgence", "partenariat", "autre"]), ephemeral=True)

    @button(label="🛡️ Application staff", style=discord.ButtonStyle.secondary, custom_id="main_staff")
    async def staff(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Quel rôle t'intéresse ?", view=TicketView(["admin", "mod", "ecoute", "propartenaire"]), ephemeral=True)

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def create_ticket(self, interaction, ticket_type):
        guild = interaction.guild
        user = interaction.user
        config = TICKETS[ticket_type]

        existing = await tickets_collection.find_one({"user_id": user.id, "closed_at": None})
        if existing:
            return await interaction.response.send_message("❌ Tu as déjà un ticket ouvert !", ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True),
        }

        if "role" in config and config["role"]:
            overwrites[guild.get_role(config["role"])] = discord.PermissionOverwrite(view_channel=True)
        elif "mentions" in config:
            for rid in config["mentions"]:
                overwrites[guild.get_role(rid)] = discord.PermissionOverwrite(view_channel=True)

        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            category=guild.get_channel(TICKET_CATEGORY_ID),
            overwrites=overwrites,
            reason=f"Ticket de {user.name}"
        )

        mention = ""
        if "role" in config and config["role"]:
            mention = f"<@&{config['role']}>"
        elif "mentions" in config:
            mention = " ".join([f"<@&{rid}>" for rid in config["mentions"]])

        embed = discord.Embed(title=config["title"], description=config["message"], color=EMBED_COLOR, timestamp=datetime.now(TIMEZONE))
        embed.set_image(url=EMBED_IMAGE_URL)

        await channel.send(f"{user.mention} bienvenue dans ton ticket !\n{mention}", embed=embed)

        await tickets_collection.insert_one({
            "channel_id": channel.id,
            "user_id": user.id,
            "username": str(user),
            "type": ticket_type,
            "opened_at": datetime.now(TIMEZONE),
            "closed_at": None
        })

        await interaction.response.send_message(f"🎟️ Ton ticket a été créé ici : {channel.mention}", ephemeral=True)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component:
            custom_id = interaction.data["custom_id"]
            if custom_id in TICKETS:
                await self.create_ticket(interaction, custom_id)

    @commands.command(name="ticketpanel")
    @commands.has_permissions(administrator=True)
    async def ticketpanel_cmd(self, ctx):
        embed = discord.Embed(
            title="🎟️ Panel des tickets",
            description="Bienvenue dans le système de ticket. Sélectionne une catégorie ci-dessous pour commencer.",
            color=EMBED_COLOR,
            timestamp=datetime.now(TIMEZONE)
        )
        embed.set_image(url=EMBED_IMAGE_URL)
        await ctx.send(embed=embed, view=MainTicketView())

    @app_commands.command(name="ticketpanel", description="Afficher le panneau de tickets")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticketpanel_slash(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎟️ Panel des tickets",
            description="Bienvenue dans le système de ticket. Sélectionne une catégorie ci-dessous pour commencer.",
            color=EMBED_COLOR,
            timestamp=datetime.now(TIMEZONE)
        )
        embed.set_image(url=EMBED_IMAGE_URL)
        await interaction.response.send_message(embed=embed, view=MainTicketView(), ephemeral=False)


    @app_commands.command(name="fermer", description="Fermer le ticket actuel")
    @app_commands.checks.has_permissions(kick_members=True)
    async def fermer_slash(self, interaction: discord.Interaction):
        if not interaction.channel.name.startswith("ticket-"):
            return await interaction.response.send_message("❌ Ce n'est pas un ticket.", ephemeral=True)
        view = ConfirmCloseView(interaction.user)
        await interaction.response.send_message("⚠️ Veux-tu vraiment fermer ce ticket ?", view=view, ephemeral=True)

class ConfirmCloseView(View):
    def __init__(self, closer):
        super().__init__(timeout=None)
        self.closer = closer

    @button(label="✅ Confirmer la fermeture", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.closer:
            return await interaction.response.send_message("Tu n'es pas autorisé à faire ça.", ephemeral=True)
        await close_ticket_static(interaction.channel, interaction.user)
        await interaction.response.send_message("✅ Ticket fermé.", ephemeral=True)

async def upload_to_sourcebin(content: str) -> str:
    async with aiohttp.ClientSession() as session:
        json_data = {
            "files": [{"content": content, "name": "transcript.txt"}],
            "title": "Transcript Ticket",
            "description": "Transcription du ticket Discord",
        }
        async with session.post("https://sourceb.in/api/bins", json=json_data) as resp:
            data = await resp.json()
            return f"https://sourceb.in/{data['key']}"

async def close_ticket_static(channel, user):
    doc = await tickets_collection.find_one({"channel_id": channel.id})
    if not doc:
        return

    log = channel.guild.get_channel(LOG_CHANNEL_ID)
    transcript, count = await generate_transcript_static(channel)
    transcript_link = await upload_to_sourcebin(transcript)

    embed = discord.Embed(title="📁 Ticket fermé", color=EMBED_COLOR, timestamp=datetime.now(TIMEZONE))
    embed.add_field(name="Type de ticket", value=TICKETS.get(doc["type"], {}).get("title", "Inconnu"), inline=True)
    embed.add_field(name="Salon", value=channel.name, inline=True)
    embed.add_field(name="Auteur", value=f"<@{doc['user_id']}>", inline=True)
    embed.add_field(name="Fermé par", value=user.mention, inline=True)
    embed.add_field(name="Messages", value=str(count), inline=True)
    embed.add_field(name="Transcript", value=f"[Voir le transcript]({transcript_link})", inline=False)
    embed.set_footer(text="Système de tickets")

    await log.send(embed=embed)
    await tickets_collection.update_one({"channel_id": channel.id}, {"$set": {"closed_at": datetime.now(TIMEZONE)}})
    await channel.delete()

async def generate_transcript_static(channel):
    messages = []
    async for msg in channel.history(limit=None, oldest_first=True):
        if not msg.author.bot:
            timestamp = msg.created_at.astimezone(TIMEZONE).strftime("%Y-%m-%d %H:%M")
            messages.append(f"[{timestamp}] {msg.author.name}: {msg.content}")
    return "\n".join(messages), len(messages)

# Setup
async def setup(bot: commands.Bot):
    await bot.add_cog(TicketSystem(bot))
