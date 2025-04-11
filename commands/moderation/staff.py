import discord
from discord.ext import commands

class StaffCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="staff")
    async def staff_formulaire(self, ctx):
        await ctx.message.delete()  # 🔥 supprime le message "!staff"

        embed = discord.Embed(
            title="📋 Formulaire de Candidature Staff",
            description=(
                "✧ **Questions à remplir pour ta candidature :**\n\n"
                "1. Quel est ton pseudo + ton âge ?\n"
                "2. Depuis combien de temps es-tu sur le serveur ?\n"
                "3. Qu’est-ce qui t’a motivé à postuler dans l’équipe ?\n"
                "4. Quelles sont, selon toi, les qualités essentielles pour ce rôle ?\n"
                "5. Comment réagirais-tu face à un conflit entre deux membres ?\n"
                "6. As-tu déjà fait partie d’un staff ailleurs ? Si oui, qu’en as-tu retiré ?\n"
                "7. Combien de temps peux-tu consacrer au serveur chaque semaine ?\n"
                "8. Tu te sens plus à l’aise en autonomie, ou en travail d’équipe ?\n"
                "9. Une petite chose à ajouter ? (compétence, idée, message…)"
            ),
            color=discord.Color.purple()
        )
        embed.set_footer(text="du staff de lonely kurozen")
        await ctx.send(embed=embed)

# Extension
async def setup(bot):
    await bot.add_cog(StaffCog(bot))
