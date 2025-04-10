import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
from dotenv import load_dotenv
import motor.motor_asyncio
from utils.rank_card import generate_rank_card


# Charger les variables d'environnement
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

client_mongo = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client_mongo[DATABASE_NAME]

level_msg_col = db["LevelUpMessages"]
user_xp_col = db["UserXP"]
rewards_col = db["LevelRewards"]
ignored_col = db["IgnoredChannels"]
xp_settings_col = db["XPSettings"]

def xp_for_next_level(level: int) -> int:
    return 5 * (level ** 2) + 50 * level + 100

async def apply_level_up_effects(member, guild, level, xp):
    try:
        config = await level_msg_col.find_one({"guild_id": guild.id})
        channel_id = config.get("channel_id") if config else None
        target_channel = guild.get_channel(channel_id) if channel_id else None

        message_template = config.get("message_template") if config else None
        message = message_template or "**{user.mention} vient de passer au niveau {level} !**"
        message = message.replace("{user.mention}", member.mention).replace("{level}", str(level)).replace("{xp}", str(xp)).replace("{server}", guild.name)

        if target_channel:
            try:
                buffer = await generate_rank_card(member, level, xp, xp_for_next_level(level + 1))
                file = discord.File(buffer, filename="rank.png")
                await target_channel.send(content=message, file=file)
            except Exception as e:
                print(f"[ERREUR CARTE] {e}")
                await target_channel.send(content=message)

        rewards_cursor = rewards_col.find({"guild_id": guild.id, "level": {"$lte": level}})
        async for reward in rewards_cursor:
            role = guild.get_role(reward["role_id"])
            if role and role not in member.roles:
                try:
                    await member.add_roles(role)
                    if target_channel:
                        await target_channel.send(f"🎉 {member.mention} a reçu le rôle **{role.name}** pour avoir atteint le niveau {level} !")
                    try:
                        await member.send(f"🎉 Tu as reçu le rôle **{role.name}** pour avoir atteint le niveau {level} !")
                    except:
                        pass
                except Exception as e:
                    print(f"[ERREUR AJOUT RÔLE] {e}")
    except Exception as e:
        print(f"[ERREUR LEVEL UP EFFECTS] {e}")

async def handle_level_up(member, guild, total_xp, current_level):
    try:
        level = current_level
        xp = total_xp
        leveled_up = False

        while xp >= xp_for_next_level(level + 1):
            xp -= xp_for_next_level(level + 1)
            level += 1
            leveled_up = True

        await user_xp_col.update_one(
            {"user_id": member.id, "guild_id": guild.id},
            {"$set": {"xp": xp, "level": level}},
            upsert=True
        )

        if leveled_up:
            await apply_level_up_effects(member, guild, level, xp)

        return level, xp
    except Exception as e:
        print(f"[ERREUR HANDLE LEVEL UP] {e}")
        return current_level, total_xp

class XPConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="xp-config", description="Configurer le système XP")
    @app_commands.checks.has_permissions(administrator=True)
    async def xp_config(self, interaction: discord.Interaction):
        try:
            embed = discord.Embed(
                title="⚙️ Configuration du système XP",
                description="Choisis une option ci-dessous pour configurer le système XP.",
                color=0x5865F2
            )
            view = ConfigMenuView(interaction.user)
            await interaction.response.send_message(embed=embed, view=view)
        except Exception as e:
            await interaction.response.send_message(f"Une erreur est survenue: {e}", ephemeral=True)

class ConfigMenuView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=180)
        self.user = user
        self.add_item(ConfigDropdown())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self.user

class ConfigDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Activer / Désactiver XP", value="toggle", emoji="⏯️"),
            discord.SelectOption(label="Message personnalisé", value="custom", emoji="📝"),
            discord.SelectOption(label="Salons ignorés", value="ignored", emoji="🚫"),
            discord.SelectOption(label="Canal level-up", value="message", emoji="🖼️"),
            discord.SelectOption(label="Récompenses de niveaux", value="rewards", emoji="🎁"),
            discord.SelectOption(label="Gestion manuelle XP", value="manual", emoji="🛠️"),
            discord.SelectOption(label="Voir les variables", value="vars", emoji="📘"),
            discord.SelectOption(label="Aide / Infos", value="help", emoji="❓"),
            discord.SelectOption(label="Reset XP du serveur", value="reset", emoji="♻️"),
        ]
        super().__init__(placeholder="Sélectionne une option", min_values=1, max_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        try:
            value = self.values[0]
            await interaction.response.defer()

            if value == "toggle":
                await toggle_xp(interaction)
            elif value == "custom":
                await handle_custom_message(interaction)
            elif value == "ignored":
                await handle_ignored(interaction)
            elif value == "message":
                await handle_message_config(interaction)
            elif value == "rewards":
                await handle_rewards(interaction)
            elif value == "manual":
                await handle_manual_xp(interaction)
            elif value == "vars":
                await show_variables(interaction)
            elif value == "help":
                await show_help(interaction)
            elif value == "reset":
                await reset_server_xp(interaction)
        except Exception as e:
            await interaction.followup.send(f"Une erreur est survenue: {e}", ephemeral=True)

# ========================
# ⏯️ Activer / Désactiver XP
# ========================
async def toggle_xp(interaction):
    try:
        guild_id = interaction.guild.id
        current = await xp_settings_col.find_one({"guild_id": guild_id}) or {"enabled": True}
        new_value = not current.get("enabled", True)

        await xp_settings_col.update_one(
            {"guild_id": guild_id},
            {"$set": {"enabled": new_value}},
            upsert=True
        )

        state = "✅ Activé" if new_value else "❌ Désactivé"
        await interaction.followup.send(f"Le système d'XP est maintenant : **{state}**")
    except Exception as e:
        await interaction.followup.send(f"Erreur: {e}", ephemeral=True)

# ========================
# 📝 Personnalisation du message de level-up (avec valeur par défaut si rien)
# ========================
async def handle_custom_message(interaction):
    try:
        guild_id = interaction.guild.id
        config = await level_msg_col.find_one({"guild_id": guild_id}) or {}
        current = config.get("message_template", "**{user.mention} vient de passer au niveau {level} !**")

        await interaction.followup.send(
            f"📩 Message actuel :\n```{current}```\n\n"
            "✏️ Tape ici le **nouveau message** à utiliser lors d'une montée de niveau.\n"
            "Tu peux utiliser les variables : `{user.mention}`, `{level}`, `{xp}`, `{server}`"
        )

        try:
            msg = await interaction.client.wait_for(
                "message", timeout=60.0,
                check=lambda m: m.author == interaction.user and m.channel == interaction.channel
            )

            await level_msg_col.update_one(
                {"guild_id": guild_id},
                {"$set": {"message_template": msg.content}},
                upsert=True
            )
            await msg.delete()
            await interaction.followup.send("✅ Message personnalisé mis à jour.")
        except asyncio.TimeoutError:
            await interaction.followup.send("⏱️ Temps écoulé.")
    except Exception as e:
        await interaction.followup.send(f"Erreur: {e}", ephemeral=True)

# ========================
# 📘 Variables disponibles
# ========================
async def show_variables(interaction):
    try:
        embed = discord.Embed(
            title="Variables disponibles",
            description="Utilisables dans les messages auto générés :",
            color=0x2b2d31
        )
        embed.add_field(name="{user.mention}", value="Mentionne l'utilisateur", inline=False)
        embed.add_field(name="{user.username}", value="Nom d'utilisateur", inline=False)
        embed.add_field(name="{member.nickname}", value="Surnom sur le serveur", inline=False)
        embed.add_field(name="{server}", value="Nom du serveur", inline=False)
        embed.add_field(name="{level}", value="Niveau atteint", inline=False)
        embed.add_field(name="{xp}", value="XP actuel", inline=False)
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"Erreur: {e}", ephemeral=True)

# ========================
# ❓ Aide / Infos
# ========================
async def show_help(interaction):
    try:
        embed = discord.Embed(title="🛠️ Aide : Configuration XP", color=discord.Color.blurple())
        embed.add_field(name="⏯️ Activer / Désactiver", value="Active ou désactive entièrement le système XP.", inline=False)
        embed.add_field(name="📝 Message personnalisé", value="Personnalise le message qui s'affiche lors d'un level-up.", inline=False)
        embed.add_field(name="🖼️ Canal level-up", value="Définit le salon où seront postées les cartes de niveau.", inline=False)
        embed.add_field(name="🚫 Salons ignorés", value="Liste les salons où aucun XP ne sera gagné.", inline=False)
        embed.add_field(name="🎁 Récompenses", value="Associe un niveau à un rôle donné automatiquement.", inline=False)
        embed.add_field(name="🛠️ Gestion manuelle XP", value="Ajoute/enlève de l'XP à un membre ou réinitialise tout.", inline=False)
        embed.add_field(name="📘 Variables", value="Liste des variables à insérer dans les messages automatiques.", inline=False)
        embed.add_field(name="♻️ Reset", value="Supprime toute l'XP du serveur (confirmation demandée).", inline=False)
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"Erreur: {e}", ephemeral=True)
# ========================
# ♻️ Reset XP du serveur
# ========================
async def reset_server_xp(interaction):
    try:
        await interaction.followup.send("⚠️ Es-tu sûr de vouloir supprimer **toute l'XP** du serveur ? Tape `CONFIRMER` pour valider.")

        try:
            msg = await interaction.client.wait_for("message", timeout=20.0, check=lambda m: m.author == interaction.user and m.channel == interaction.channel)
            if msg.content.upper() == "CONFIRMER":
                await user_xp_col.delete_many({"guild_id": interaction.guild.id})
                await msg.delete()
                await interaction.followup.send("✅ XP de tous les membres supprimée.")
            else:
                await msg.delete()
                await interaction.followup.send("❌ Annulé.")
        except asyncio.TimeoutError:
            await interaction.followup.send("⏱️ Temps écoulé.")
    except Exception as e:
        await interaction.followup.send(f"Erreur: {e}", ephemeral=True)

# ========================
# 🛠️ Gestion manuelle XP
# ========================
async def handle_manual_xp(interaction):
    guild = interaction.guild
    guild_id = guild.id
    channel = interaction.channel

    await channel.send("Tape `add`, `delete` ou `reset`.")

    try:
        msg = await interaction.client.wait_for("message", timeout=30.0, check=lambda m: m.author == interaction.user and m.channel == channel)
        action = msg.content.lower()
        await msg.delete()

        if action in ["add", "delete"]:
            await channel.send("Mentionne un membre.")
            user_msg = await interaction.client.wait_for("message", timeout=30.0, check=lambda m: m.author == interaction.user and m.channel == channel)
            if not user_msg.mentions:
                await channel.send("❌ Aucun membre mentionné.")
                return
            member = user_msg.mentions[0]
            await user_msg.delete()

            await channel.send("Combien d’XP ?")
            xp_msg = await interaction.client.wait_for("message", timeout=30.0, check=lambda m: m.author == interaction.user and m.channel == channel)
            if not xp_msg.content.isdigit():
                await channel.send("❌ Valeur XP invalide.")
                return
            amount = int(xp_msg.content)
            await xp_msg.delete()

            user_data = await user_xp_col.find_one({"guild_id": guild_id, "user_id": member.id}) or {"xp": 0, "level": 0}
            xp = user_data["xp"]
            level = user_data["level"]

            if action == "add":
                xp += amount
            else:
                xp = max(0, xp - amount)

            # Recalcul + effets
            level, xp = await handle_level_up(member, guild, xp, level)
            await channel.send(f"{member.mention} → {xp} XP | Niveau {level}")

        elif action == "reset":
            await user_xp_col.delete_many({"guild_id": guild_id})
            await channel.send("XP réinitialisé pour tous.")

        else:
            await channel.send("❌ Action inconnue.")
    except asyncio.TimeoutError:
        await channel.send("⏱️ Temps écoulé.")

# ========================
# 🎁 Récompenses de niveau (ajout, suppression, liste)
# ========================
async def handle_rewards(interaction):
    try:
        guild_id = interaction.guild.id
        channel = interaction.channel

        await channel.send("Tape `set` pour ajouter, `remove` pour supprimer, ou `list` pour afficher les récompenses.")

        try:
            msg = await interaction.client.wait_for("message", timeout=30.0, check=lambda m: m.author == interaction.user and m.channel == channel)
            action = msg.content.lower()
            await msg.delete()

            if action == "set":
                await channel.send("Niveau requis ?")
                lvl_msg = await interaction.client.wait_for("message", timeout=30.0, check=lambda m: m.author == interaction.user and m.channel == channel)
                if not lvl_msg.content.isdigit():
                    await channel.send("❌ Niveau invalide.")
                    return
                level = int(lvl_msg.content)
                await lvl_msg.delete()

                await channel.send("Mentionne le rôle.")
                role_msg = await interaction.client.wait_for("message", timeout=30.0, check=lambda m: m.author == interaction.user and m.channel == channel)
                if role_msg.role_mentions:
                    role = role_msg.role_mentions[0]
                    await rewards_col.update_one(
                        {"guild_id": guild_id, "level": level},
                        {"$set": {"role_id": role.id}},
                        upsert=True
                    )
                    await role_msg.reply(f"🎁 Récompense ajoutée : {role.mention} au niveau {level}")
                await role_msg.delete()

            elif action == "remove":
                await channel.send("Niveau à retirer ?")
                lvl_msg = await interaction.client.wait_for("message", timeout=30.0, check=lambda m: m.author == interaction.user and m.channel == channel)
                if not lvl_msg.content.isdigit():
                    await channel.send("❌ Niveau invalide.")
                    return
                level = int(lvl_msg.content)
                await lvl_msg.delete()

                await rewards_col.delete_one({"guild_id": guild_id, "level": level})
                await channel.send(f"🗑️ Récompense supprimée pour le niveau {level}")

            elif action == "list":
                cursor = rewards_col.find({"guild_id": guild_id}).sort("level", 1)
                rewards = await cursor.to_list(length=50)

                if not rewards:
                    await channel.send("Aucune récompense définie.")
                    return

                desc = ""
                for reward in rewards:
                    role = interaction.guild.get_role(reward["role_id"])
                    role_name = role.mention if role else f"(rôle introuvable `{reward['role_id']}`)"
                    desc += f"Niveau **{reward['level']}** → {role_name}\n"

                embed = discord.Embed(title="🎁 Récompenses configurées", description=desc, color=0x00ffcc)
                await channel.send(embed=embed)

            else:
                await channel.send("❌ Commande inconnue. Utilise `set`, `remove`, ou `list`.")

        except asyncio.TimeoutError:
            await channel.send("⏱️ Temps écoulé.")
    except Exception as e:
        await interaction.followup.send(f"Erreur: {e}", ephemeral=True)

# ========================
# 🚫 Salons ignorés
# ========================
async def handle_ignored(interaction):
    try:
        guild_id = interaction.guild.id
        channel = interaction.channel

        await channel.send("Tape `add`, `remove`, ou `list`.")

        try:
            msg = await interaction.client.wait_for("message", timeout=30.0, check=lambda m: m.author == interaction.user and m.channel == channel)
            cmd = msg.content.lower()
            await msg.delete()

            if cmd == "add":
                await channel.send("Mentionne le salon à ajouter.")
                ch_msg = await interaction.client.wait_for("message", timeout=30.0, check=lambda m: m.author == interaction.user and m.channel == channel)
                if ch_msg.channel_mentions:
                    ch = ch_msg.channel_mentions[0]
                    await ignored_col.update_one(
                        {"guild_id": guild_id},
                        {"$addToSet": {"channels": ch.id}},
                        upsert=True
                    )
                    await ch_msg.reply(f"{ch.mention} ajouté.")
                await ch_msg.delete()

            elif cmd == "remove":
                await channel.send("Mentionne le salon à retirer.")
                ch_msg = await interaction.client.wait_for("message", timeout=30.0, check=lambda m: m.author == interaction.user and m.channel == channel)
                if ch_msg.channel_mentions:
                    ch = ch_msg.channel_mentions[0]
                    await ignored_col.update_one(
                        {"guild_id": guild_id},
                        {"$pull": {"channels": ch.id}}
                    )
                    await ch_msg.reply(f"{ch.mention} retiré.")
                await ch_msg.delete()

            elif cmd == "list":
                doc = await ignored_col.find_one({"guild_id": guild_id})
                if doc and "channels" in doc:
                    mentions = [interaction.guild.get_channel(cid).mention for cid in doc["channels"] if interaction.guild.get_channel(cid)]
                    await channel.send("Salons ignorés : " + ", ".join(mentions) if mentions else "Aucun salon ignoré.")
                else:
                    await channel.send("Aucun salon ignoré.")
            else:
                await channel.send("❌ Commande non reconnue.")
        except asyncio.TimeoutError:
            await channel.send("⏱️ Temps écoulé.")
    except Exception as e:
        await interaction.followup.send(f"Erreur: {e}", ephemeral=True)

# ========================
# 🖼️ Définir le canal level-up
# ========================
async def handle_message_config(interaction):
    try:
        guild_id = interaction.guild.id
        channel = interaction.channel

        await channel.send("Mentionne le salon où envoyer les cartes de level-up :")

        try:
            msg = await interaction.client.wait_for("message", timeout=30.0, check=lambda m: m.author == interaction.user and m.channel == channel)
            if not msg.channel_mentions:
                await channel.send("❌ Aucune mention détectée.")
                return
            target_channel = msg.channel_mentions[0]
            await msg.delete()

            await level_msg_col.update_one(
                {"guild_id": guild_id},
                {"$set": {"channel_id": target_channel.id}},
                upsert=True
            )
            await channel.send(f"✅ Salon de level-up défini : {target_channel.mention}")

        except asyncio.TimeoutError:
            await channel.send("⏱️ Temps écoulé.")
    except Exception as e:
        await interaction.followup.send(f"Erreur: {e}", ephemeral=True)


# ========================
# 📥 Setup du cog 
# ========================


async def setup(bot: commands.Bot):
    await bot.add_cog(XPConfig(bot))  # Ajoute ton cog normalement
