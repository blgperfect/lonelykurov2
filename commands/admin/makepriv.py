import os, re, asyncio, discord, motor.motor_asyncio, locale, datetime
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

client_mongo = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client_mongo[DATABASE_NAME]
private_rooms_col = db["private_rooms"]

try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except:
    pass

def parse_duration(duration_str: str) -> int:
    match = re.fullmatch(r"(\d+)([smhd])", duration_str)
    if not match:
        return None
    value, unit = match.groups()
    value = int(value)
    multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    return value * multipliers[unit]

PERMISSION_LABELS = {
    "view_channel": "Voir le salon",
    "send_messages": "Envoyer des messages",
    "read_message_history": "Lire l'historique",
    "embed_links": "Envoyer des liens",
    "attach_files": "Envoyer des fichiers",
    "manage_channels": "Gérer l’accès",
    "manage_permissions": "Gérer les permissions",
    "manage_messages": "Gérer les messages"
}

class PermissionSelectionView(discord.ui.View):
    def __init__(self, guild: discord.Guild):
        super().__init__(timeout=120)
        self.member_perms = []
        self.guild = guild
        self.ready = asyncio.Event()

        self.perm_select = discord.ui.Select(
            placeholder="Permissions du membre",
            min_values=1,
            max_values=len(PERMISSION_LABELS),
            options=[
                discord.SelectOption(label=PERMISSION_LABELS[k], value=k)
                for k in PERMISSION_LABELS
            ]
        )
        self.perm_select.callback = self.perm_select_callback
        self.add_item(self.perm_select)

    async def perm_select_callback(self, interaction: discord.Interaction):
        self.member_perms = self.perm_select.values
        await interaction.response.defer()

    @discord.ui.button(label="✅ Valider", style=discord.ButtonStyle.green)
    async def validate_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.member_perms:
            await interaction.response.send_message("❌ Sélectionne au moins une permission.", ephemeral=True)
        else:
            await interaction.response.send_message("✅ Permissions enregistrées.", ephemeral=True)
            self.ready.set()

class PrivateRoomsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="make-private", description="Créer un salon privé pour un membre")
    @app_commands.describe(
        membre="Le membre pour qui créer le salon privé",
        catégorie="La catégorie où créer le salon privé",
        raison="La raison de la création du salon",
        temp="Durée (formats : s, m, h, d). Ex : 10m, 2h"
    )
    async def make_private(self, interaction: discord.Interaction, membre: discord.Member,
                           catégorie: discord.CategoryChannel, raison: str, temp: str = None):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Vous devez être administrateur.", ephemeral=True)
            return

        await interaction.response.defer(thinking=True, ephemeral=True)
        guild = interaction.guild

        existing = await private_rooms_col.find_one({
            "guildId": str(guild.id),
            "userId": str(membre.id)
        })
        if existing:
            return await interaction.followup.send("❌ Ce membre a déjà un salon privé actif.", ephemeral=True)

        duration_seconds = None
        expiration_dt = None
        if temp:
            duration_seconds = parse_duration(temp)
            if duration_seconds is None:
                embed = discord.Embed(
                    title="⏱️ Format de durée invalide",
                    description="Ex : `10m`, `2h`, `1d` — s: sec, m: min, h: heure, d: jour",
                    color=0xE74C3C
                )
                return await interaction.followup.send(embed=embed, ephemeral=True)
            expiration_dt = datetime.datetime.now() + datetime.timedelta(seconds=duration_seconds)

        view = PermissionSelectionView(guild)
        await interaction.followup.send("🔧 Choisissez les permissions :", view=view, ephemeral=True)
        try:
            await view.ready.wait()
        except asyncio.TimeoutError:
            return await interaction.followup.send("⏳ Temps écoulé. Action annulée.", ephemeral=True)

        perms_dict = {perm: (perm in view.member_perms) for perm in PERMISSION_LABELS}
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                view_channel=True,
                read_message_history=True,
                send_messages=False
            ),
            membre: discord.PermissionOverwrite(**perms_dict),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }

        try:
            channel_name = membre.display_name.lower().replace(" ", "-")
            private_channel = await guild.create_text_channel(
                name=channel_name,
                category=catégorie,
                overwrites=overwrites,
                reason=f"Salon privé pour {membre} | {raison}"
            )
        except Exception as e:
            print(f"[Erreur création salon] {e}")
            return await interaction.followup.send("❌ Erreur lors de la création du salon.", ephemeral=True)

        room_doc = {
            "guildId": str(guild.id),
            "userId": str(membre.id),
            "channelId": str(private_channel.id),
            "reason": raison,
            "timestamp": datetime.datetime.now().isoformat(),
            "expiration": expiration_dt.isoformat() if expiration_dt else None
        }
        await private_rooms_col.insert_one(room_doc)

        dispo_str = f"<t:{int(expiration_dt.timestamp())}:F>" if expiration_dt else "Indéfini"
        perms_text = "\n".join(f"✅ {PERMISSION_LABELS.get(p)}" for p in view.member_perms)

        await private_channel.send(f"{membre.mention}")

        welcome_embed = discord.Embed(
            description=(
                f"👤 **Salon Perso :** {membre.mention}\n"
                f"🗓️ **Valable jusqu'à :** {dispo_str}\n"
                f"🔎 **Raison :** {raison}\n\n"
                f"🛠️ **Permissions :**\n{perms_text}"
            ),
            color=0x1abc9c
        )
        await private_channel.send(embed=welcome_embed)

        if duration_seconds:
            await private_channel.send(f"⏳ Ce salon sera supprimé dans `{temp}`.")

            async def auto_delete():
                await asyncio.sleep(duration_seconds)
                chan = guild.get_channel(private_channel.id)
                if chan:
                    try:
                        await chan.delete(reason="Suppression automatique du salon privé")
                    except Exception as e:
                        print(f"[Erreur suppression auto] {e}")
                await private_rooms_col.delete_one({
                    "guildId": str(guild.id),
                    "userId": str(membre.id)
                })

            self.bot.loop.create_task(auto_delete())

        success_embed = discord.Embed(
            title="✅ Salon privé créé",
            description=(
                f"Le salon {private_channel.mention} a été créé pour {membre.mention} "
                f"dans la catégorie {catégorie.mention}."
            ),
            color=0x2ECC71
        )
        await interaction.followup.send(embed=success_embed, ephemeral=True)

    @app_commands.command(name="delete-private", description="Supprimer le salon privé d'un membre")
    async def delete_private(self, interaction: discord.Interaction, membre: discord.Member):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Vous devez être administrateur.", ephemeral=True)
            return

        await interaction.response.defer(thinking=True, ephemeral=True)
        guild = interaction.guild
        room_doc = await private_rooms_col.find_one({
            "guildId": str(guild.id),
            "userId": str(membre.id)
        })

        if not room_doc:
            return await interaction.followup.send("❌ Aucun salon trouvé pour ce membre.", ephemeral=True)

        channel = guild.get_channel(int(room_doc["channelId"]))
        if not channel:
            await private_rooms_col.delete_one({
                "guildId": str(guild.id),
                "userId": str(membre.id)
            })
            return await interaction.followup.send("⚠️ Le salon n'existe plus, supprimé de la base.", ephemeral=True)

        try:
            await channel.delete(reason="Suppression via /delete-private")
            await private_rooms_col.delete_one({
                "guildId": str(guild.id),
                "userId": str(membre.id)
            })
            await interaction.followup.send(f"✅ Salon de {membre.mention} supprimé.", ephemeral=True)
        except Exception as e:
            print(f"[Erreur suppression salon] {e}")
            await interaction.followup.send("❌ Erreur lors de la suppression.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(PrivateRoomsCog(bot))