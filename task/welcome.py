import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_channel_id = 1348173789585997909  # Vérifie que c’est bon sur ton nouveau serveur
        self.role_to_ping_id = 1348573308609888276     # Idem pour ce rôle
        self.image_url = "https://cdn.discordapp.com/attachments/1102406059722801184/1360130394950729868/B783042A-505F-499D-967E-2B73D7F14529.png?ex=67f9ffa4&is=67f8ae24&hm=1121478965f1dba828400d0cee17d72025662fa2c4462af0884df6762bcd5d65&"

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        channel = guild.get_channel(self.welcome_channel_id)
        role_mention = f"<@&{self.role_to_ping_id}>"

        if channel:
            embed = discord.Embed(
                title="𖥔・𝑩𝒊𝒆𝒏𝒗𝒆𝒏𝒖𝒆 𝒔𝒖𝒓 𝐋𝐎𝐍𝐄𝐋𝐘 𝐊𝐔𝐑𝐎𝐙𝐄𝐍・𖥔",
                description=(
                    "˚　 ⋆⁺₊✦⁺₊ 　 ˚　.˚ .　 ☁.　　. 　 ˚　⁺⋆₊　.˚　.　. ✦⋆⁺₊ 　 ˚　. ☁ ˚　.˚　 ✩₊˚. ☾ ⋆ ⁺₊✧  　　˚　⁺₊ . 　 ˚　.　　⁺₊✦₊　　 ☁ 　˚　　 . 　⁺₊✧˚　　 . 　 ˚　⁺₊˚ .\n\n"
                    "Une présence vient de traverser le voile…\n"
                    "Bienvenue à toi, voyageur des étoiles.\n\n"
                    "Ici, chaque âme est libre d’évoluer à son rythme — entre discussions, chill, vibes cosmiques et magie partagée.\n\n"
                    "→ N’oublie pas de choisir tes rôles dans les salons prévus\n"
                    "→ Consulte le règlement pour que l’énergie reste paisible\n"
                    "→ Et surtout… prends ta place parmi nous\n\n"
                    "Le sanctuaire t’est désormais ouvert. ✦"
                ),
                color=discord.Color.from_str("#C9B6D9")
            )
            embed.set_image(url=self.image_url)
            embed.set_footer(
                text=f"Avec toi nous sommes maintenant {guild.member_count}",
                icon_url=self.bot.user.display_avatar.url
            )

            await channel.send(
                content=f"{role_mention} {member.mention}",
                embed=embed
            )

        # MP
        try:
            dm_embed = discord.Embed(
                title="𖥔・Server Alliance・𖥔",
                description=(
                    "Un serveur actif où tu peux gagner des abonnements en toute simplicité.\n"
                    "🌸 Esprit chill, des Giveaways Fast, entraide & bonne vibe — que tu sois en vocal ou en texte, t’es jamais seul.\n"
                    "🎮 Communauté gaming & giveaways rapides\n\n"
                    "→ **https://discord.gg/9fSybhuxV6**"
                ),
                color=discord.Color.from_str("#C9B6D9")
            )
            await member.send(embed=dm_embed)
        except discord.Forbidden:
            pass

async def setup(bot):
    await bot.add_cog(Welcome(bot))
