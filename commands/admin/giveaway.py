import discord
from discord.ext import commands
from discord import app_commands
import asyncio, random, re, os
import motor.motor_asyncio
from dotenv import load_dotenv

load_dotenv()

# Récupérer les variables nécessaires
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# Connexion MongoDB
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DATABASE_NAME]

# Collection spécifique
giveaway_col = db["giveaways"]

class GiveawayView(discord.ui.View):
    def __init__(self, message_id, max_participants, bot):
        super().__init__(timeout=None)
        self.message_id = message_id
        self.max_participants = max_participants
        self.bot = bot

    @discord.ui.button(label="🎉 Participer", style=discord.ButtonStyle.green, custom_id="join_giveaway")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        doc = await giveaway_col.find_one({"message_id": self.message_id})
        if not doc:
            return await interaction.response.send_message("❌ Giveaway introuvable.", ephemeral=True)

        if str(interaction.user.id) in doc["participants"]:
            return await interaction.response.send_message("❌ Tu participes déjà !", ephemeral=True)

        if doc.get("max_participants") and len(doc["participants"]) >= doc["max_participants"]:
            return await interaction.response.send_message("❌ Limite de participants atteinte !", ephemeral=True)

        doc["participants"].append(str(interaction.user.id))
        await giveaway_col.update_one({"message_id": self.message_id}, {"$set": {"participants": doc["participants"]}})

        channel = self.bot.get_channel(doc["channel_id"])
        msg = await channel.fetch_message(self.message_id)
        embed = msg.embeds[0]
        embed.set_footer(text=f"Participants : {len(doc['participants'])}/{doc.get('max_participants') or '∞'}")
        await msg.edit(embed=embed)

        await interaction.response.send_message("✅ Participation enregistrée !", ephemeral=True)

        if doc.get("max_participants") and len(doc["participants"]) >= doc["max_participants"]:
            for child in self.children:
                if child.custom_id == "join_giveaway":
                    child.disabled = True
            await msg.edit(view=self)

    @discord.ui.button(label="❔ Aide", style=discord.ButtonStyle.blurple, custom_id="help_giveaway")
    async def help(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Clique sur 🎉 pour participer ! Le tirage se fait automatiquement à la fin du temps imparti. Bonne chance !",
            ephemeral=True
        )

    @discord.ui.button(label="🛑 Annuler (Admin)", style=discord.ButtonStyle.red, custom_id="cancel_giveaway")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message("❌ Tu n'as pas la permission d'annuler ce giveaway.", ephemeral=True)

        doc = await giveaway_col.find_one({"message_id": self.message_id})
        if not doc:
            return await interaction.response.send_message("❌ Giveaway introuvable ou déjà terminé.", ephemeral=True)

        channel = self.bot.get_channel(doc["channel_id"])
        message = await channel.fetch_message(self.message_id)
        embed = discord.Embed(
            title=f"🚫 Giveaway annulé : {doc['lot']}",
            description="Ce giveaway a été annulé par un administrateur.",
            color=discord.Color.red()
        )
        await message.edit(embed=embed, view=None)
        await giveaway_col.delete_one({"message_id": self.message_id})
        await interaction.response.send_message("🛑 Giveaway annulé avec succès.", ephemeral=True)

class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="giveaway", description="Lancer un giveaway")
    @app_commands.describe(
        lot="Nom du lot à gagner",
        description="Description du lot",
        gagnants="Nombre de gagnants",
        duree="Durée (ex: 10s, 1m, 1h, 1d)",
        salon="Salon où envoyer le giveaway",
        limite_participants="Nombre max de participants (optionnel)"
    )
    async def giveaway(self, interaction: discord.Interaction, lot: str, description: str, gagnants: int, duree: str, salon: discord.TextChannel, limite_participants: int = None):
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message("❌ Permission refusée.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        seconds = self.parse_duration(duree)
        if seconds is None:
            return await interaction.followup.send("❌ Format de durée invalide. Utilise s, m, h ou d (ex: 2m, 1h).", ephemeral=True)

        embed = discord.Embed(
            title=f"🎉 Giveaway : {lot}",
            description=description,
            color=discord.Color.gold()
        )
        embed.add_field(name="Nombre de gagnants", value=str(gagnants))
        embed.set_footer(text=f"Participants : 0/{limite_participants or '∞'}")

        message = await salon.send(embed=embed, view=GiveawayView(message_id=0, max_participants=limite_participants, bot=self.bot))

        await giveaway_col.insert_one({
            "message_id": message.id,
            "channel_id": salon.id,
            "guild_id": interaction.guild.id,
            "lot": lot,
            "description": description,
            "gagnants": gagnants,
            "participants": [],
            "max_participants": limite_participants
        })

        view = GiveawayView(message_id=message.id, max_participants=limite_participants, bot=self.bot)
        await message.edit(view=view)

        await interaction.followup.send(f"✅ Giveaway lancé dans {salon.mention} pour `{duree}`.", ephemeral=True)
        await asyncio.sleep(seconds)
        await self.finish_giveaway(message.id)

    async def finish_giveaway(self, message_id):
        doc = await giveaway_col.find_one({"message_id": message_id})
        if not doc:
            return

        channel = self.bot.get_channel(doc["channel_id"])
        message = await channel.fetch_message(message_id)
        participants = [self.bot.get_user(int(uid)) for uid in doc["participants"]]
        winners = random.sample(participants, doc["gagnants"]) if len(participants) >= doc["gagnants"] else participants

        mentions = ", ".join(w.mention for w in winners) if winners else "Aucun gagnant."
        embed = discord.Embed(
            title=f"🏆 Giveaway terminé : {doc['lot']}",
            description=f"🎉 Gagnants : {mentions}\nMerci d'avoir participé !",
            color=discord.Color.green()
        )
        await message.edit(embed=embed, view=None)
        await channel.send(f"🎉 Félicitations {mentions} ! Vous avez gagné : **{doc['lot']}**")
        await giveaway_col.delete_one({"message_id": message_id})

    def parse_duration(self, duree: str):
        match = re.match(r"^(\d+)([smhd])$", duree.lower())
        if not match:
            return None
        value = int(match.group(1))
        unit = match.group(2)
        return value * {"s": 1, "m": 60, "h": 3600, "d": 86400}[unit]

async def setup(bot):
    await bot.add_cog(Giveaways(bot))
