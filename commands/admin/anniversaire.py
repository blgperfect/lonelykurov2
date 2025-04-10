import discord, asyncio, os, re
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timedelta, date
import motor.motor_asyncio
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client["kurozen_system"]  # ✅ tu forces l'accès à cette base ici
birthdays_col = db["birthdays"]
birthday_config_col = db["birthday_config"]


class BirthdayView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.add_item(BirthdayButton("🎂 S’inscrire", "register"))
        self.add_item(BirthdayButton("✏️ Modifier", "edit"))
        self.add_item(BirthdayButton("📅 Prochains anniversaires", "list"))
        self.add_item(BirthdayButton("🛠️ Configurer le salon", "config", admin_only=True))
        self.add_item(BirthdayButton("🧪 Tester une annonce", "test", admin_only=True))

class BirthdayButton(discord.ui.Button):
    def __init__(self, label, action, admin_only=False):
        style = discord.ButtonStyle.danger if admin_only else discord.ButtonStyle.primary
        super().__init__(label=label, style=style, custom_id=action)
        self.admin_only = admin_only

    async def callback(self, interaction: discord.Interaction):
        if self.admin_only and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("🚫 Réservé aux admins.", ephemeral=True)
        await handle_button(interaction, self.custom_id)

async def handle_button(interaction: discord.Interaction, action: str):
    if action in ["register", "edit"]:
        await interaction.response.send_modal(BirthdayModal(edit=(action=="edit")))
    elif action == "list":
        await show_upcoming(interaction)
    elif action == "config":
        await interaction.response.send_message("Mentionne le salon souhaité pour les annonces d’anniversaire :", ephemeral=True)
        def check(m): return m.author == interaction.user and m.channel == interaction.channel
        try:
            msg = await interaction.client.wait_for("message", timeout=30, check=check)
            if not msg.channel_mentions:
                return await interaction.followup.send("❌ Mention de salon invalide.", ephemeral=True)
            channel = msg.channel_mentions[0]
            await birthday_config_col.update_one(
                {"guild_id": interaction.guild.id},
                {"$set": {"channel_id": channel.id}},
                upsert=True
            )
            await interaction.followup.send(f"✅ Salon configuré : {channel.mention}")
        except asyncio.TimeoutError:
            await interaction.followup.send("⏰ Temps écoulé.", ephemeral=True)
    elif action == "test":
        await simulate_announcement(interaction)

class BirthdayModal(discord.ui.Modal):
    def __init__(self, edit=False):
        super().__init__(title="✏️ Modifier ton anniversaire" if edit else "🎂 S’inscrire")
        self.date_input = discord.ui.TextInput(
            label="Date de naissance",
            placeholder="Ex: 19/01/2001",
            max_length=10
        )
        self.add_item(self.date_input)

    async def on_submit(self, interaction: discord.Interaction):
        match = re.match(r"^(\d{2})/(\d{2})/(\d{4})$", self.date_input.value)
        if not match:
            return await interaction.response.send_message("❌ Format invalide. Utilise JJ/MM/AAAA", ephemeral=True)
        try:
            datetime.strptime(self.date_input.value, "%d/%m/%Y")
        except:
            return await interaction.response.send_message("❌ Date invalide.", ephemeral=True)

        await birthdays_col.update_one(
            {"user_id": str(interaction.user.id)},
            {"$set": {"birthday": self.date_input.value}},
            upsert=True
        )
        await interaction.response.send_message("✅ Date enregistrée !", ephemeral=True)

async def show_upcoming(interaction: discord.Interaction):
    today = date.today()
    upcoming = []
    async for doc in birthdays_col.find({}):
        try:
            user = interaction.guild.get_member(int(doc["user_id"]))
            if not user: continue
            d = datetime.strptime(doc["birthday"], "%d/%m/%Y").date().replace(year=today.year)
            if d < today: d = d.replace(year=today.year + 1)
            upcoming.append((user, d))
        except:
            continue
    upcoming.sort(key=lambda x: x[1])
    embed = discord.Embed(title="📅 Prochains anniversaires", color=discord.Color.blurple())
    lines = [f"{u.mention} – {d.strftime('%d/%m')} (**dans {(d - today).days}j**)" for u, d in upcoming[:10]]
    embed.description = "\n".join(lines) or "Aucun membre avec une date connue dans ce serveur."
    await interaction.response.send_message(embed=embed)

async def simulate_announcement(interaction: discord.Interaction):
    config = await birthday_config_col.find_one({"guild_id": interaction.guild.id})
    if not config or not config.get("channel_id"):
        return await interaction.response.send_message("❌ Aucun salon configuré.", ephemeral=True)
    channel = interaction.guild.get_channel(config["channel_id"])
    if not channel:
        return await interaction.response.send_message("❌ Salon introuvable.", ephemeral=True)
    embed = discord.Embed(
        title="🎉 Joyeux anniversaire !",
        description=f"Félicitations à {interaction.user.mention} pour son anniversaire aujourd'hui !",
        color=discord.Color.green()
    )
    await channel.send(embed=embed)
    await interaction.response.send_message("✅ Test envoyé dans le salon.", ephemeral=True)

class BirthdayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_birthdays.start()

    @tasks.loop(hours=1)
    async def check_birthdays(self):
        today = datetime.utcnow().date()
        async for doc in birthdays_col.find({}):
            try:
                d = datetime.strptime(doc["birthday"], "%d/%m/%Y").date()
                if d.day != today.day or d.month != today.month:
                    continue
                for guild in self.bot.guilds:
                    member = guild.get_member(int(doc["user_id"]))
                    if not member:
                        continue
                    config = await birthday_config_col.find_one({"guild_id": guild.id})
                    if not config: continue
                    channel = guild.get_channel(config.get("channel_id"))
                    if channel:
                        embed = discord.Embed(
                            title="🎉 Joyeux anniversaire !",
                            description=f"C’est l’anniversaire de {member.mention} aujourd’hui !",
                            color=discord.Color.green()
                        )
                        await channel.send(embed=embed)
            except Exception as e:
                print(f"[BirthdayCheckError] {e}")

    @app_commands.command(name="anniversaire_panel", description="Affiche le panneau anniversaire")
    @app_commands.checks.has_permissions(administrator=True)
    async def anniversaire_panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎂 Panneau Anniversaire",
            description="Gère les inscriptions, la config et les annonces pour les anniversaires.",
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed, view=BirthdayView(self.bot))

async def setup(bot: commands.Bot):
    await bot.add_cog(BirthdayCog(bot))