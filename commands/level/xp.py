import discord
from discord.ext import commands
from discord import app_commands
import random
import motor.motor_asyncio
import os
from dotenv import load_dotenv
from utils.rank_card import generate_rank_card, generate_leaderboard_image
import asyncio
from datetime import datetime, timedelta


# ENV
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

client_mongo = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client_mongo[DATABASE_NAME]

user_xp_col = db["UserXP"]
level_msg_col = db["LevelUpMessages"]
rewards_col = db["LevelRewards"]
ignored_channels_col = db["IgnoredChannels"]
xp_settings_col = db["XPSettings"]
cooldowns = {}  # Pour éviter le spam XP

def xp_for_next_level(level: int) -> int:
    return 5 * (level ** 2) + 50 * level + 100

async def apply_level_up_effects(member, guild, level, xp):
    try:
        config = await level_msg_col.find_one({"guild_id": guild.id})
        channel_id = config.get("channel_id") if config else None
        target_channel = guild.get_channel(channel_id) if channel_id else None

        # Message personnalisé
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
                # Envoyer quand même le message si la carte échoue
                await target_channel.send(content=message)

        # Attribution des récompenses
        rewards_cursor = rewards_col.find({"guild_id": guild.id, "level": {"$lte": level}})
        async for reward in rewards_cursor:
            role = guild.get_role(reward["role_id"])
            if role and role not in member.roles:
                try:
                    await member.add_roles(role)
                    if target_channel:
                        await target_channel.send(f"🎁 {member.mention} a reçu le rôle **{role.name}** !")
                    try:
                        await member.send(f"🎁 Tu as reçu le rôle **{role.name}** pour avoir atteint le niveau {level} !")
                    except:
                        pass
                except Exception as e:
                    print(f"[ERREUR RÔLE] {e}")
    except Exception as e:
        print(f"[ERREUR LEVEL UP] {e}")

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

        # N'appliquer les effets que si l'utilisateur a gagné un niveau
        if leveled_up:
            await apply_level_up_effects(member, guild, level, xp)
            
        return level, xp
    except Exception as e:
        print(f"[ERREUR HANDLE LEVEL UP] {e}")
        return current_level, total_xp

class XP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldown = 60  # Cooldown en secondes

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        # Check if XP is enabled
        try:
            xp_config = await xp_settings_col.find_one({"guild_id": message.guild.id})
            if xp_config and not xp_config.get("enabled", True):
                return

            # Ignored channels
            ignored = await ignored_channels_col.find_one({"guild_id": message.guild.id})
            if ignored and message.channel.id in ignored.get("channels", []):
                return

            # Anti-spam cooldown
            user_id = message.author.id
            guild_id = message.guild.id
            cooldown_key = f"{user_id}_{guild_id}"
            
            current_time = datetime.now()
            if cooldown_key in cooldowns:
                time_diff = (current_time - cooldowns[cooldown_key]).total_seconds()
                if time_diff < self.cooldown:
                    return  # Encore en cooldown
            
            # Mise à jour du cooldown
            cooldowns[cooldown_key] = current_time
            
            # Nettoyage des anciens cooldowns (tous les 100 messages)
            if len(cooldowns) > 100:
                old_time = current_time - timedelta(seconds=self.cooldown)
                cooldowns_to_remove = [k for k, v in cooldowns.items() if v < old_time]
                for k in cooldowns_to_remove:
                    del cooldowns[k]

            # Gain aléatoire
            xp_gain = random.randint(5, 15)
            user_data = await user_xp_col.find_one({"user_id": message.author.id, "guild_id": message.guild.id})

            if not user_data:
                user_data = {"user_id": message.author.id, "guild_id": message.guild.id, "xp": 0, "level": 0}
                await user_xp_col.insert_one(user_data)

            new_xp = user_data["xp"] + xp_gain
            await handle_level_up(message.author, message.guild, new_xp, user_data["level"])
        except Exception as e:
            print(f"[ERREUR ON_MESSAGE] {e}")

    @app_commands.command(name="lvl", description="Affiche votre niveau")
    async def lvl(self, interaction: discord.Interaction, member: discord.Member = None):
        try:
            member = member or interaction.user
            data = await user_xp_col.find_one({"user_id": member.id, "guild_id": interaction.guild.id})

            if not data:
                buffer = await generate_rank_card(member, 0, 0, xp_for_next_level(1))
            else:
                xp = data["xp"]
                level = data["level"]
                buffer = await generate_rank_card(member, level, xp, xp_for_next_level(level + 1))

            file = discord.File(buffer, filename="rank.png")
            await interaction.response.send_message(file=file)
        except Exception as e:
            await interaction.response.send_message(f"Une erreur est survenue: {e}", ephemeral=True)

    @app_commands.command(name="xp-leaderboard", description="Classement des meilleurs XP (serveur)")
    async def leaderboard(self, interaction: discord.Interaction):
        try:
            cursor = user_xp_col.find({"guild_id": interaction.guild.id}).sort([("level", -1), ("xp", -1)])
            raw_data = await cursor.to_list(length=10)

            if not raw_data:
                await interaction.response.send_message("Aucun utilisateur trouvé.", ephemeral=True)
                return

            members_data = []
            for entry in raw_data:
                member = interaction.guild.get_member(entry["user_id"])
                if member:
                    total_xp = sum(xp_for_next_level(lvl) for lvl in range(entry["level"])) + entry["xp"]
                    members_data.append({
                        "name": member.display_name,
                        "level": entry["level"],
                        "total_xp": total_xp,
                        "avatar": member.display_avatar
                    })

            if not members_data:
                await interaction.response.send_message("Aucun utilisateur trouvé.")
                return

            image = await generate_leaderboard_image(members_data)
            file = discord.File(image, filename="leaderboard.png")
            embed = discord.Embed(title="Classement XP", color=discord.Color.fuchsia())
            embed.set_image(url="attachment://leaderboard.png")
            await interaction.response.send_message(embed=embed, file=file)
        except Exception as e:
            await interaction.response.send_message(f"Une erreur est survenue: {e}", ephemeral=True)

    @app_commands.command(name="xp-global", description="Classement XP global (tous serveurs)")
    async def global_leaderboard(self, interaction: discord.Interaction):
        try:
            # Utiliser l'agrégation pour éviter les duplications d'utilisateurs
            pipeline = [
                {"$group": {
                    "_id": "$user_id",
                    "total_level": {"$sum": "$level"},
                    "total_xp": {"$sum": "$xp"}
                }},
                {"$sort": {"total_level": -1, "total_xp": -1}},
                {"$limit": 10}
            ]
            
            cursor = user_xp_col.aggregate(pipeline)
            raw_data = await cursor.to_list(length=10)

            if not raw_data:
                await interaction.response.send_message("Aucun utilisateur trouvé.", ephemeral=True)
                return

            members_data = []
            for entry in raw_data:
                user = self.bot.get_user(entry["_id"])
                if user:
                    # Calculer le total XP incluant les niveaux complétés
                    xp_total = entry["total_xp"] + sum(xp_for_next_level(lvl) for lvl in range(entry["total_level"]))
                    members_data.append({
                        "name": user.name,
                        "level": entry["total_level"],
                        "total_xp": xp_total,
                        "avatar": user.display_avatar
                    })

            if not members_data:
                await interaction.response.send_message("Aucun utilisateur trouvé.")
                return

            image = await generate_leaderboard_image(members_data)
            file = discord.File(image, filename="global_leaderboard.png")
            embed = discord.Embed(title="Classement XP Global", color=discord.Color.gold())
            embed.set_image(url="attachment://global_leaderboard.png")
            await interaction.response.send_message(embed=embed, file=file)
        except Exception as e:
            await interaction.response.send_message(f"Une erreur est survenue: {e}", ephemeral=True)




async def setup(bot: commands.Bot):
    await bot.add_cog(XP(bot))  # XP ou XPConfig selon ton fichier



