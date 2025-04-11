import discord
from discord.ext import commands
from discord.ui import View, Button

class NewButtons(View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(Button(label="Récompenses / Privilèges", emoji="🎁", custom_id="privilege", style=discord.ButtonStyle.primary))
        self.add_item(Button(label="Nouveautés récentes", emoji="🆕", custom_id="nouveaute", style=discord.ButtonStyle.primary))


class NewCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="new")
    async def new_command(self, ctx):
        await ctx.message.delete()

        embed = discord.Embed(
            title="𖥔・Menu du sanctuaire・𖥔",
            description=(
                "Bienvenue dans le cœur de lonely kurozen…\n"
                "Ici, tu trouveras toutes les informations utiles ainsi que les privilèges liés au serveur.\n\n"
                "Pour en savoir plus, sélectionne simplement l’un des boutons ci-dessus ^-^"
            ),
            color=discord.Color.purple()
        )
        embed.set_image(url="https://media.discordapp.net/attachments/1102406059722801184/1360331053969051842/BB629ED8-5F8F-4CD9-92DA-987EB13A8F2E.png?ex=67faba84&is=67f96904&hm=609058489666f05ffcd06c0fecb0aaec584acabe48cc9fe53bfe5ffbf03d5b82&=&format=webp&quality=lossless&width=722&height=722")
        embed.set_footer(text="lonely kurozen — cœur du sanctuaire")

        await ctx.send(embed=embed, view=NewButtons())

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if not interaction.type == discord.InteractionType.component:
            return

        custom_id = interaction.data["custom_id"]

        if custom_id == "privilege":
            embed = discord.Embed(
                title="𖥔・Récompenses du Sanctuaire・𖥔",
                description=(
                    "Une mise à jour des privilèges offerts aux membres méritants…\n\n"
                    "⸻\n\n"
                    "✦ Boosters du serveur\n\n"
                    "Les membres qui boostent lonely kurozen bénéficient de privilèges exclusifs.\n"
                    "Un tri régulier est effectué pour s’assurer que seuls les vrais boosters conservent ces avantages, afin de respecter l’esprit de ces récompenses.\n\n"
                    "Voici ce que vous débloquez en tant que booster :\n\n"
                    "1. Rôle personnalisé\n"
                    "→ Choisissez le nom, la couleur et l’émoji de votre rôle. (sous réserve que le niveau de boost le permette)\n\n"
                    "2. Salon privé entre boosters\n"
                    "→ Un espace dédié uniquement aux membres qui boostent le serveur.\n\n"
                    "3. Salon privé personnalisé\n"
                    "→ Sur demande via ticket, vous pouvez obtenir un salon privé, avec les membres de votre choix, et définir qui peut lire, écrire, etc.\n"
                    "→ Ce salon peut durer 1 semaine, 2 semaines ou plus, selon l’usage et notre appréciation du projet.\n\n"
                    "4. Giveaways surprises\n"
                    "→ Des cadeaux inattendus pour remercier votre soutien.\n\n"
                    "⸻\n\n"
                    "✦ Récompenses par niveau\n\n"
                    "Pour le moment, aucune récompense liée aux niveaux n’est active.\n"
                    "Mais comme on dit… les suggestions sont faites pour ça !\n"
                    "→ Si tu as des idées, n’hésite pas à proposer !"
                ),
                color=discord.Color.purple()
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1102406059722801184/1360330706827350056/7CEF6500-343C-4D1E-8B69-3636FBE83B13.png?ex=67faba32&is=67f968b2&hm=15ed0b28b66b13e0381ecb49539925e4968495a1b3d5e0a349d4c7a950eb5e73&=&format=webp&quality=lossless&width=618&height=618")
            await interaction.response.send_message(embed=embed, ephemeral=True)

        elif custom_id == "nouveaute":
            embed = discord.Embed(
                title="𖥔・Mise à jour du Sanctuaire・𖥔",
                description=(
                    "Un vent de renouveau souffle sur lonely kurozen…\n\n"
                    "⸻\n\n"
                    "✦ Nouveau bot officiel : Kurozen\n\n"
                    "Notre serveur possède désormais son propre bot personnalisé.\n"
                    "Toutes les commandes principales, notamment de modération, passent désormais par lui.\n\n"
                    "⸻\n\n"
                    "✦ Nouvelle identité visuelle\n\n"
                    "Comme voté, lonely kurozen adopte désormais un thème entièrement violet !\n\n"
                    "Nouvelle photo de serveur, nouvelle bannière… tout est aligné avec votre choix !\n\n"
                    "⸻\n\n"
                    "✦ Quelles nouveautés concrètes ?\n\n"
                    "⭐️ Starboard\n"
                    "→ Si un message reçoit 5 réactions avec l’emoji ⭐️, il apparaîtra automatiquement dans le salon #starboard.\n\n"
                    "Attention, de petits bugs peuvent encore survenir, comme un message affiché deux fois (on blame l’étoile aveugle…).\n\n"
                    "📈 Système de niveau amélioré\n"
                    "→ Gagnez de l’XP en parlant, débloquez des rôles et suivez votre évolution.\n"
                    "→ Nouveauté : réalisez de petits succès personnels et soyez notifié lorsqu’un est accompli !\n\n"
                    "🎮 Carte de niveau enrichie\n"
                    "→ Elle affiche désormais :\n"
                    "\t•\tVotre nombre total de messages (depuis l’enregistrement du bot)\n"
                    "\t•\tVotre temps passé en vocal\n\n"
                    "⸻\n\n"
                    "✦ /report obligatoire pour les signalements\n\n"
                    "À partir de maintenant, tous les signalements de membres doivent passer par la commande :\n"
                    "/report\n\n"
                    "Merci d’indiquer le pseudo exact + preuve (image)\n"
                    "Ces signalements sont privés, visibles uniquement par le staff.\n\n"
                    "⸻\n\n"
                    "Un grand merci à tous ceux qui font vivre ce sanctuaire.\n"
                    "Et ce n’est que le début… restez à l’écoute."
                ),
                color=discord.Color.purple()
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1102406059722801184/1360330707402227752/CD4BE6F2-F858-4FDA-9C8E-44C91C1121B3.png?ex=67faba32&is=67f968b2&hm=edf2e09f4ea2a75d6db8fb9a7c00ed575cfef5b3f3ea900a27874b73c1992738&=&format=webp&quality=lossless&width=618&height=618")
            await interaction.response.send_message(embed=embed, ephemeral=True)

# Extension
async def setup(bot):
    await bot.add_cog(NewCog(bot))
