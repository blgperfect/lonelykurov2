import discord
from discord.ext import commands
from datetime import datetime

# === CONFIGURATION ===
STARBOARD_CHANNEL_ID = 1360088840429371463
STAR_EMOJI = "⭐"
STAR_THRESHOLD = 5
EMBED_COLOR = discord.Color.gold()

class StarboardTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.starred_messages = set()  # ⛔ Empêche les doublons

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        # Ignore si autre emoji
        if str(payload.emoji) != STAR_EMOJI:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        # Ignore les bots
        if message.author.bot:
            return

        # Si déjà starboardé
        if message.id in self.starred_messages:
            return

        # Compte les ⭐
        star_count = 0
        for reaction in message.reactions:
            if str(reaction.emoji) == STAR_EMOJI:
                star_count = reaction.count
                break

        if star_count < STAR_THRESHOLD:
            return

        # Ajoute à la liste pour bloquer les doublons
        self.starred_messages.add(message.id)

        # Envoi dans le salon starboard
        starboard_channel = guild.get_channel(STARBOARD_CHANNEL_ID)
        embed = discord.Embed(
            title="🌟 Message populaire",
            description=message.content or "*Aucun contenu texte*",
            color=EMBED_COLOR,
            timestamp=message.created_at
        )
        embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed.add_field(name="🔗 Lien", value=f"[Aller au message]({message.jump_url})", inline=False)
        embed.set_footer(text=f"Posté dans #{channel.name} • {star_count}⭐")

        await starboard_channel.send(embed=embed)

# === EXTENSION ===
async def setup(bot):
    await bot.add_cog(StarboardTask(bot))
