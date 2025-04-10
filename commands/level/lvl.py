import discord
from discord import app_commands
from discord.ext import commands
import motor.motor_asyncio
from dotenv import load_dotenv
from utils.rank_card import generate_rank_card
import os

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DATABASE_NAME]
user_collection = db["users"]

LEVEL_ROLES = {
    1: 1359707224255107312,
    5: 1359707497107165336,
    15: 1359707724170137680,
    25: 1359707998490071190,
    50: 1359708925082992880,
    70: 1359709378357231646,
    100: 1359709836908036257,
}

class Level(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="lvl", description="Affiche ta carte de niveau.")
    @app_commands.describe(member="Le membre à consulter.")
    async def lvl(self, interaction: discord.Interaction, member: discord.Member = None):
        await interaction.response.defer()
        member = member or interaction.user
        guild = interaction.guild
        user_id = str(member.id)
        guild_id = str(guild.id)

        user_data = await user_collection.find_one({"user_id": user_id, "guild_id": guild_id})
        if not user_data:
            await user_collection.insert_one({
                "user_id": user_id,
                "guild_id": guild_id,
                "xp": 0,
                "level": 1,
                "messages": 0,
                "vocal_minutes": 0
            })
            user_data = await user_collection.find_one({"user_id": user_id, "guild_id": guild_id})

        xp = user_data.get("xp", 0)
        level = user_data.get("level", 1)
        total_messages = user_data.get("messages", 0)
        total_vocal = user_data.get("vocal_minutes", 0)
        next_level_xp = 100 + (level * 100)

        # Mise à jour des rôles en fonction du niveau actuel :
        role_to_add = None
        for lvl_threshold in sorted(LEVEL_ROLES.keys()):
            role = guild.get_role(LEVEL_ROLES[lvl_threshold])
            if level >= lvl_threshold:
                role_to_add = role
        roles_to_remove = []
        for lvl_threshold in LEVEL_ROLES:
            role = guild.get_role(LEVEL_ROLES[lvl_threshold])
            if role in member.roles and role != role_to_add:
                roles_to_remove.append(role)
        if role_to_add and role_to_add not in member.roles:
            await member.add_roles(role_to_add)
        for role in roles_to_remove:
            await member.remove_roles(role)

        card_image = await generate_rank_card(
            member=member,
            level=level,
            xp=xp,
            next_level_xp=next_level_xp,
            total_messages=total_messages,
            total_vocal=total_vocal
        )

        file = discord.File(card_image, filename="rank.png")
        await interaction.followup.send(file=file)

async def setup(bot: commands.Bot):
    await bot.add_cog(Level(bot))
