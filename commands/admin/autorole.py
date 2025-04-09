# commands that can be use for global bot / commands qui peux etre utulisé dans un bot globale.
import os
import discord
from discord import app_commands
from discord.ext import commands
import motor.motor_asyncio
import asyncio
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
client_mongo = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client_mongo[DATABASE_NAME]
role_auto_col = db["role_auto"]

def create_embed(title: str, description: str, color: int = 0x1abc9c) -> discord.Embed:
    return discord.Embed(title=title, description=description, color=color)

async def wait_for_message(interaction: discord.Interaction, prompt: str, timeout=60):
    try:
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(prompt, ephemeral=True)
        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel
        msg = await interaction.client.wait_for("message", check=check, timeout=timeout)
        return msg.content.strip()
    except asyncio.TimeoutError:
        await interaction.followup.send(embed=create_embed("Erreur", "⏰ Temps écoulé."), ephemeral=True)
        return None

class RoleAutoMenuView(discord.ui.View):
    def __init__(self, author, cog):
        super().__init__(timeout=120)
        self.author = author
        self.cog = cog

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message(embed=create_embed("Erreur", "Ce menu ne t’appartient pas."), ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Ajouter un rôle", style=discord.ButtonStyle.primary, custom_id="roleauto_add")
    async def btn_add(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.flow_add(interaction)

    @discord.ui.button(label="Ajouter plusieurs rôles", style=discord.ButtonStyle.primary, custom_id="roleauto_multi")
    async def btn_multi(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.flow_multi(interaction)

    @discord.ui.button(label="Lister les rôles", style=discord.ButtonStyle.secondary, custom_id="roleauto_list")
    async def btn_list(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.flow_list(interaction)

    @discord.ui.button(label="Supprimer un rôle", style=discord.ButtonStyle.danger, custom_id="roleauto_remove")
    async def btn_remove(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.flow_remove(interaction)
class RoleAutoCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="role-auto", description="Gère l’auto-attribution de rôles à l’arrivée")
    @app_commands.checks.has_permissions(administrator=True)
    async def role_auto(self, interaction: discord.Interaction):
        view = RoleAutoMenuView(interaction.user, self)
        embed = create_embed("Système de Rôles Automatiques", 
                             "Choisis une action :\n• Ajouter un rôle\n• Ajouter plusieurs rôles\n• Lister les rôles\n• Supprimer un rôle")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def flow_add(self, interaction: discord.Interaction):
        role_input = await wait_for_message(interaction, "Mentionne le rôle à ajouter (ex: @NomDuRole ou ID) :")
        if not role_input:
            return
        role_obj = None
        if role_input.startswith("<@&") and role_input.endswith(">"):
            try:
                role_id = int(role_input.strip("<@&>"))
                role_obj = interaction.guild.get_role(role_id)
            except:
                pass
        else:
            try:
                role_id = int(role_input)
                role_obj = interaction.guild.get_role(role_id)
            except:
                pass
        if not role_obj:
            await interaction.followup.send(embed=create_embed("Erreur", "Rôle introuvable."), ephemeral=True)
            return
        type_input = await wait_for_message(interaction, "Entrez le type de rôle (membre ou bot) :")
        if not type_input:
            return
        type_input = type_input.lower()
        if type_input not in ["membre", "bot"]:
            await interaction.followup.send(embed=create_embed("Erreur", "Le type doit être membre ou bot."), ephemeral=True)
            return
        try:
            guild_data = await role_auto_col.find_one({"guildId": str(interaction.guild.id)}) or {"guildId": str(interaction.guild.id), "membre": [], "bot": []}
            if role_obj.id in guild_data.get(type_input, []):
                await interaction.followup.send(embed=create_embed("Erreur", f"Ce rôle est déjà configuré pour les {type_input}s."), ephemeral=True)
                return
            guild_data[type_input].append(role_obj.id)
            await role_auto_col.update_one({"guildId": str(interaction.guild.id)}, {"$set": guild_data}, upsert=True)
            await interaction.followup.send(embed=create_embed("✅ Rôle ajouté", 
                f"Le rôle {role_obj.mention} a été ajouté pour les {type_input}s."), ephemeral=True)
        except Exception as e:
            print(e)

    async def flow_multi(self, interaction: discord.Interaction):
        roles_input = await wait_for_message(interaction, "Entrez les rôles à ajouter, séparés par des virgules :")
        if not roles_input:
            return
        role_parts = [r.strip() for r in roles_input.split(",")]
        role_ids = []
        for part in role_parts:
            role_obj = None
            if part.startswith("<@&") and part.endswith(">"):
                try:
                    role_id = int(part.strip("<@&>"))
                    role_obj = interaction.guild.get_role(role_id)
                except:
                    continue
            else:
                try:
                    role_id = int(part)
                    role_obj = interaction.guild.get_role(role_id)
                except:
                    continue
            if role_obj:
                role_ids.append(role_obj.id)
        if not role_ids:
            await interaction.followup.send(embed=create_embed("Erreur", "Aucun rôle valide trouvé."), ephemeral=True)
            return
        type_input = await wait_for_message(interaction, "Entrez le type de rôle (membre ou bot) :")
        if not type_input:
            return
        type_input = type_input.lower()
        if type_input not in ["membre", "bot"]:
            await interaction.followup.send(embed=create_embed("Erreur", "Le type doit être membre ou bot."), ephemeral=True)
            return
        try:
            guild_data = await role_auto_col.find_one({"guildId": str(interaction.guild.id)}) or {"guildId": str(interaction.guild.id), "membre": [], "bot": []}
            added_roles = []
            already_configured = []
            for rid in role_ids:
                if rid in guild_data.get(type_input, []):
                    already_configured.append(f"<@&{rid}>")
                else:
                    guild_data[type_input].append(rid)
                    added_roles.append(f"<@&{rid}>")
            await role_auto_col.update_one({"guildId": str(interaction.guild.id)}, {"$set": guild_data}, upsert=True)
            if added_roles:
                msg = f"Les rôles suivants ont été ajoutés : {', '.join(added_roles)}"
            else:
                msg = "Aucun nouveau rôle ajouté."
            await interaction.followup.send(embed=create_embed("✅ Ajout terminé", msg), ephemeral=True)
        except Exception as e:
            print(e)
    async def flow_list(self, interaction: discord.Interaction):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)
        try:
            guild_data = await role_auto_col.find_one({"guildId": str(interaction.guild.id)})
            if not guild_data or (not guild_data.get("membre") and not guild_data.get("bot")):
                await interaction.followup.send(embed=create_embed("Erreur", "Aucun rôle automatique configuré."), ephemeral=True)
                return
            membre_roles = guild_data.get("membre", [])
            bot_roles = guild_data.get("bot", [])
            membre_list = ", ".join(f"<@&{rid}>" for rid in membre_roles) if membre_roles else "Aucun"
            bot_list = ", ".join(f"<@&{rid}>" for rid in bot_roles) if bot_roles else "Aucun"
            msg = f"**Membres** : {membre_list}\n**Bots** : {bot_list}"
            await interaction.followup.send(embed=create_embed("📋 Liste des rôles automatiques", msg), ephemeral=True)
        except Exception as e:
            print(e)

    async def flow_remove(self, interaction: discord.Interaction):
        roles_input = await wait_for_message(interaction, "Entrez les rôles à retirer, séparés par des virgules :")
        if not roles_input:
            return
        role_parts = [r.strip() for r in roles_input.split(",")]
        role_ids = []
        for part in role_parts:
            try:
                role_id = int(part.strip("<@&>")) if "<@&" in part else int(part)
                role_ids.append(role_id)
            except:
                continue
        type_input = await wait_for_message(interaction, "Entrez le type de rôle à retirer (membre ou bot) :")
        if not type_input:
            return
        type_input = type_input.lower()
        if type_input not in ["membre", "bot"]:
            await interaction.followup.send(embed=create_embed("Erreur", "Le type doit être membre ou bot."), ephemeral=True)
            return
        try:
            guild_data = await role_auto_col.find_one({"guildId": str(interaction.guild.id)})
            if not guild_data:
                await interaction.followup.send(embed=create_embed("Erreur", "Aucun rôle automatique n’est configuré."), ephemeral=True)
                return
            removed_roles = []
            for rid in role_ids:
                if rid in guild_data.get(type_input, []):
                    guild_data[type_input].remove(rid)
                    removed_roles.append(f"<@&{rid}>")
            await role_auto_col.update_one({"guildId": str(interaction.guild.id)}, {"$set": guild_data})
            msg = f"Rôles retirés : {', '.join(removed_roles)}" if removed_roles else "Aucun rôle retiré."
            await interaction.followup.send(embed=create_embed("✅ Suppression", msg), ephemeral=True)
        except Exception as e:
            print(e)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        try:
            guild_data = await role_auto_col.find_one({"guildId": str(member.guild.id)})
            if not guild_data:
                return
            roles = guild_data.get("bot", []) if member.bot else guild_data.get("membre", [])
            role_objects = [member.guild.get_role(rid) for rid in roles if member.guild.get_role(rid)]
            if role_objects:
                await member.add_roles(*role_objects, reason="Attribution automatique de rôles")
        except Exception as e:
            print(e)

async def setup(bot: commands.Bot):
    await bot.add_cog(RoleAutoCog(bot))
