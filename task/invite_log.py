import discord
from discord.ext import commands, tasks
from datetime import datetime

# === CONFIGURATION ===
INVITE_LOG_CHANNEL = 1359653014058569757  # Salon de log des invitations

class InviteTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invites = {}  # guild.id : list of invites

    @commands.Cog.listener()
    async def on_ready(self):
        print("🔄 Initialisation du suivi des invitations...")
        for guild in self.bot.guilds:
            self.invites[guild.id] = await guild.invites()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self.bot.wait_until_ready()
        guild = member.guild
        before_invites = self.invites.get(guild.id, [])
        after_invites = await guild.invites()

        used_invite = None
        inviter = None

        for invite in after_invites:
            old = discord.utils.get(before_invites, code=invite.code)
            if old and invite.uses > old.uses:
                used_invite = invite
                inviter = invite.inviter
                break

        self.invites[guild.id] = after_invites

        channel = guild.get_channel(INVITE_LOG_CHANNEL)
        if not channel:
            return

        # === MESSAGE FINAL ===
        if inviter:
            total_invites = sum(i.uses for i in after_invites if i.inviter == inviter)
            embed = discord.Embed(
                title="📥 Nouvelle arrivée",
                description=(
                    f"{member.mention} a rejoint le serveur.\n"
                    f"👤 Invité par **{inviter.mention}**\n"
                    f"🎟️ Nombre total d'invitations : **{total_invites}**"
                ),
                color=discord.Color.blurple(),
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=f"ID du membre : {member.id}")
        else:
            embed = discord.Embed(
                title="📥 Nouvelle arrivée",
                description=(
                    f"{member.mention} a rejoint le serveur, mais l'invitation utilisée n'a pas pu être déterminée."
                ),
                color=discord.Color.greyple(),
                timestamp=datetime.utcnow()
            )

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        self.invites[invite.guild.id] = await invite.guild.invites()

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        self.invites[invite.guild.id] = await invite.guild.invites()

# === EXTENSION ===
async def setup(bot):
    await bot.add_cog(InviteTracker(bot))
