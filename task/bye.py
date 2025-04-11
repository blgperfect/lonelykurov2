import discord
from discord.ext import commands

class Bye(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bye_channel_id = 1348180843083989053  # Salon pour les messages d’au revoir

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild = member.guild
        channel = guild.get_channel(self.bye_channel_id)

        if channel:
            embed = discord.Embed(
                title="𖥔・Un voyageur a quitté le sanctuaire・𖥔",
                description=(
                    f"{member.mention} nous a quitté !\n"
                    f"Nous sommes maintenant **{guild.member_count}** membres !\n\n"
                    f"**ID du membre** : `{member.id}`\n"
                    f"**Nom (non mentionné)** : `{member}`"
                ),
                color=discord.Color.from_str("#C9B6D9")
            )
            embed.set_footer(
                text="À bientôt, peut-être...",
                icon_url=self.bot.user.display_avatar.url
            )

            await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Bye(bot))
